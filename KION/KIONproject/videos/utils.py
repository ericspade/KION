import hashlib
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
import os
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json


# Kafka
producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "deduplication_events")


def dedup_request(timeout=10, persist_days=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method != "POST" or request.content_type != "application/json":
                return view_func(request, *args, **kwargs)

            try:
                body = json.loads(request.body.decode("utf-8"))
                key_fields = ["userId", "content_id", "event_name", "event_datetime", "sid"]
                key_data = ":".join(str(body.get(f, "")) for f in key_fields)
                dedupe_key = hashlib.sha256(key_data.encode()).hexdigest()

                payload = {
                    "dedupe_key": dedupe_key,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": body,
                    "expires_at": (datetime.utcnow() + timedelta(days=persist_days)).isoformat()
                    if persist_days else None
                }

                producer.send(KAFKA_TOPIC, value=payload)
                producer.flush()

                if cache.get(dedupe_key):
                    return JsonResponse({"status": "duplicate", "dedupe_key": dedupe_key}, status=200)
                cache.set(dedupe_key, True, timeout)

            except Exception as e:
                print("Ошибка целостности JSON:", e)
                return JsonResponse({"error": "Сервер не отвечает или битый JSON"}, status=400)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
