from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from hashlib import sha256
import os, json
from kafka import KafkaProducer
import redis
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

srvlogs = []


def add_log(message):
    if len(srvlogs) >= 100:
        srvlogs.pop(0)
    srvlogs.append(message)


# Redis
redis_client = redis.Redis(host="192.168.0.112", port=6379, db=0)

# Kafka
producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dedup_events")
CACHE_TIMEOUT = 604800
PERSIST_DAYS = 7


class EventModel(BaseModel):
    platform: str
    event_name: str
    profile_age: int
    user_agent: str
    screen: str
    event_datetime_str: str
    event_datetime: str
    event_date: str
    auth_method: str
    auth_type: str
    request_id: str
    referer: str
    subscription_name: str
    subscription_id: str
    deeplink: str
    payment_type: str
    transaction_id: str
    purchase_option: str
    content_type: str
    content_gid: str
    content_name: str
    content_id: str
    promocode: str
    promocode_code: str
    quality: str
    play_url: str
    channel_name: str
    channel_id: str
    channel_gid: str
    cause: str
    button_id: str
    button_text: str
    feedback_text: str
    experiments: str
    season: str
    episode: str
    discount_items_ids: str
    discount_items_names: str
    content_provider: str
    story_type: str
    userId: str
    playtime_ms: int
    duration: int
    client_id: str
    discount: str
    is_trial: bool
    price: int
    dt_add: str
    url_user_event: str
    event_receive_timestamp: int
    event_receive_dt_str: str
    shelf_name: str
    shelf_index: int
    card_index: int
    error_message: str
    platform_useragent: str
    product_id: str
    dl: str
    fp: str
    dr: str
    mc: str
    r: str
    sc: int
    sid: str
    sr: str
    title: str
    ts: str
    wr: str
    cid: str
    uid: str
    ll: str
    av: str
    os: str
    mnf: str
    mdl: str
    os_family: str
    os_version: str
    is_mobile: bool
    is_pc: bool
    is_tablet: bool
    is_touch_capable: bool
    client_id_body: str
    client_id_query: str
    time: int
    field_id: str
    field_action: str
    search_films: str
    recommended_films: str
    event_datetime_msc: str
    user_device_is_tv: bool
    input_type: str
    product_names: str
    product_ids: str
    prices: str
    auth_status_list: str
    isJunior: str
    waterbase_device_id: str
    error_url: str
    error_severity: int
    error_category: int
    error_code: str
    os_build: str
    banner_type: str
    banner_id: str
    banner_gid: str
    kion_session_id: str
    popup_name: str
    popup_action: str
    app_version: str
    downloaded: int
    osv: str
    dt: str
    dm: str
    lc: str
    event_source: str
    device_id: str
    debug: bool
    host: str
    path: str
    request_type: str
    code: str
    message: str
    field_text: str
    card_gid: str
    current_time: str
    card_id: str
    card_type: str
    card_name: str
    uuid: str
    term: str
    playing_mode: str
    inserted_dt: str
    build_model: str
    build_manufacturer: str
    extra_field: str
    trouble_report: str
    playback_speed: str


@app.post("/api-fast/view-event")
async def view_event(event: EventModel, request: Request):
    key_fields = [event.userId, event.content_id, event.event_name, event.event_datetime, event.sid]
    key_string = ":".join(key_fields)
    dedupe_key = sha256(key_string.encode()).hexdigest()

    pipe = redis_client.pipeline()
    pipe.get(dedupe_key)
    pipe.setex(dedupe_key, CACHE_TIMEOUT, 1)
    get_result, _ = pipe.execute()

    if get_result:
        print(f"[Дубликат] Найдено то же событие:  {dedupe_key} в {datetime.utcnow().isoformat()}")
        add_log(f"[Дубликат] Найдено то же событие:  {dedupe_key} в {datetime.utcnow().isoformat()}")
        return {"status": "duplicate", "dedupe_key": dedupe_key}

    payload = {
        "dedupe_key": dedupe_key,
        "timestamp": datetime.utcnow().isoformat(),
        "data": event.dict(),

    }

    producer.send(KAFKA_TOPIC, value=payload)
    print(f"[Новое событие] Уникальное событие {dedupe_key} записывается в основную БД {datetime.utcnow().isoformat()}")
    add_log(f"[Новое событие] Уникальное событие {dedupe_key} записывается в основную БД {datetime.utcnow().isoformat()}")


@app.get("/api-fast/status")
async def get_status():
    return {"srvlogs": srvlogs}
