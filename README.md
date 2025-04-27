## Дедупликатор событий

Здравствуйте!

Здесь вы можете найти билд дедубликатора событий.
Билд выдерживает около 1000 RPS согласно Locust.

![image](https://github.com/user-attachments/assets/f2486876-b1ef-45ff-bf67-126e2369dec4)



## Инструкция по деплою:

1. Клонируйте этот python-проект
2. Установите Kafka, Zookeeper и Postgres как контейнеры Docker на локальной машине следующими 3мя командами:
   
      `docker run -d --name kafka --network kafka-net -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -p 9092:9092 confluentinc/cp-kafka:latest`
   
      `docker exec kafka kafka-topics --create --topic dedup_events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1`
   
      `docker run --name pg-json -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=dbadmin -e POSTGRES_DB=kion -p 5432:5432 -d postgres:16`
   
   (Тонкой настройки контейнеров не требуется)

3. Я использовал Redis для кэширования хэшей установленный как отдельная VMWare вирт. машина
   
   <ins>Образ:</ins> Ubuntu 24.10 Live Server

   <ins>Настройка сети:</ins> Bridged + Replicate physical network connection state

   **Установите Ubuntu в vmware workstation и в него redis-server(порт 6379):**

         sudo apt install redis-server

         sudo systemctl enable redis

         sudo systemctl start redis

         sudo apt install net-tools

      (что бы проверить работу):
         `netstat -an | grep 6379`

      <ins>В конфиге /etc/redis/redis.conf:</ins> измените bind на 'bind 0.0.0.0' и 'protected-mode yes' на 'protected-mode no'

      Запустите монитор событий:

         redis-cli monitor


5. Установите все нужные зависимости в python проект и запустите 3 отдельных сервиса (в 3х терминалах):
   
   `python manage.py runserver`
   
   `python kafkacons.py`
   
   `uvicorn fastapi_server:app --host 0.0.0.0 --port 8001 --workers 4`


## API эндпоинт:

   **http://<ip локальной машины>:8001/api-fast/view-event**


## Все нужные порты:

   **8000 (Django)**

   **8001 (FastAPI/uvicorn)**

   **9092 (Kafka)**

   **5432 (Postgres)**

   **6379 (Redis)**

## Алгоритм:

   1. На эндпоинт поступает JSON-событие в формате предоставленного образца (136 отдельных полей; поля в форматах string, int и bool).
   2. На основе полей **userId**, **content_id**, **event_name**, **event_datetime** и **sid** поступившего события генерируется хэш типа sha256.
   3. Из кэша Redis (на отдельной машине) запрашивается полученный хэш и если он находится то событие считается дубликатом и в консоль/лог выдается соответствующее сообщение (дальнейшие действия по обработке события прекращаются). 
   
   Если совпадение хэшу в Redis не найдено:
   
   4. Полученный хэш сохраняется в кэш Redis сроком на 7 дней.
   5. JSON события целиком отправляется в очередь Kafka для последующей записи события в бессрочную базу данных Postgres (Kafk'ой. Основной микросервис дальше не участвует в обработке и берется за следующее событие).  
   6. В консоль/лог выдается сообщение о новом событии и его записи в основную БД.

## Нагрузочный тестинг:

Для нагрузочного тестирования использовался следующий locustfile.py скрипт
В него дублируются системные логи (обрабатываемых событий), их можно наблюдать во вкладке LOGS (открыв браузерный интерфейс locust'а)

# locustfile.py

`from locust import HttpUser, task, between
import uuid
import random
from datetime import datetime
import json
import logging

logger = logging.getLogger("locust")

class FastAPITestUser(HttpUser):
    wait_time = between(0.001, 0.005)`

    @task(5)
    def send_event(self):
        now = datetime.utcnow()
        iso_now = now.isoformat() + "Z"
        sample_payload = {
            "platform": "androidtv",
            "event_name": "app_list100000001",
            "profile_age": -1,
            "user_agent": "ru.mts.mtstv/1.1.137.74.6.1(20240214)",
            "screen": "",
            "event_datetime_str": now.strftime("%Y-%m-%d %H:%M:%S"),
            "event_datetime": iso_now,
            "event_date": now.strftime("%Y-%m-%d"),
            "auth_method": "",
            "auth_type": "",
            "request_id": str(uuid.uuid4().hex),
            "referer": "",
            "subscription_name": "",
            "subscription_id": "",
            "deeplink": "",
            "payment_type": "",
            "transaction_id": "",
            "purchase_option": "",
            "content_type": "",
            "content_gid": "",
            "content_name": "",
            "content_id": "",
            "promocode": "",
            "promocode_code": "",
            "quality": "",
            "play_url": "",
            "channel_name": "",
            "channel_id": "",
            "channel_gid": "",
            "cause": "",
            "button_id": "",
            "button_text": "",
            "feedback_text": "",
            "experiments": "",
            "season": "",
            "episode": "",
            "discount_items_ids": "",
            "discount_items_names": "",
            "content_provider": "",
            "story_type": "",
            "userId": str(uuid.uuid4()),
            "playtime_ms": 2000245,
            "duration": 52355567,
            "client_id": str(uuid.uuid4().hex),
            "discount": "",
            "is_trial": False,
            "price": 0,
            "dt_add": iso_now,
            "url_user_event": "",
            "event_receive_timestamp": int(datetime.utcnow().timestamp()),
            "event_receive_dt_str": now.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "shelf_name": "",
            "shelf_index": 1,
            "card_index": 1,
            "error_message": "",
            "platform_useragent": "",
            "product_id": str(uuid.uuid4()),
            "dl": "",
            "fp": "",
            "dr": "",
            "mc": "",
            "r": str(random.randint(1000000000, 9999999999)),
            "sc": 1,
            "sid": str(random.randint(1000000000, 9999999999)),
            "sr": "1920x1080",
            "title": "",
            "ts": iso_now,
            "wr": "",
            "cid": "",
            "uid": str(uuid.uuid4()),
            "ll": "",
            "av": "",
            "os": "Android",
            "mnf": "SDMC",
            "mdl": "DV9135",
            "os_family": "Other",
            "os_version": "",
            "is_mobile": True,
            "is_pc": True,
            "is_tablet": True,
            "is_touch_capable": True,
            "client_id_body": "",
            "client_id_query": str(uuid.uuid4().hex),
            "time": 0,
            "field_id": "",
            "field_action": "",
            "search_films": "",
            "recommended_films": "",
            "event_datetime_msc": iso_now,
            "user_device_is_tv": True,
            "input_type": "",
            "product_names": "",
            "product_ids": "",
            "prices": "",
            "auth_status_list": "",
            "isJunior": "",
            "waterbase_device_id": "5C7B5C5D47CD",
            "error_url": "",
            "error_severity": 999,
            "error_category": 999,
            "error_code": "",
            "os_build": "",
            "banner_type": "",
            "banner_id": "",
            "banner_gid": "",
            "kion_session_id": "5C7B5C5D47CD",
            "popup_name": "",
            "popup_action": "",
            "app_version": "1.1.137.74.6.1",
            "downloaded": 25,
            "osv": "",
            "dt": "",
            "dm": "",
            "lc": "",
            "event_source": "",
            "device_id": "",
            "debug": False,
            "host": "",
            "path": "",
            "request_type": "",
            "code": "",
            "message": "",
            "field_text": "",
            "card_gid": "",
            "current_time": now.strftime("%Y-%m-%d"),
            "card_id": "",
            "card_type": "",
            "card_name": "",
            "uuid": str(uuid.uuid4()),
            "term": "",
            "playing_mode": "",
            "inserted_dt": iso_now,
            "build_model": "DV9135",
            "build_manufacturer": "SDMC",
            "extra_field": "",
            "trouble_report": "",
            "playback_speed": ""
        }
        self.client.post("/api-fast/view-event", json=sample_payload)

    @task(1)
    def get_status(self):
        with self.client.get("/api-fast/status", catch_response=True) as response:
            if response.status_code == 200:
                logs = response.json().get("srvlogs", [])
                if logs:
                    logger.info(f": {logs[-1]}")
            else:
                logger.error(f"Ошибка эндпоинта /status: {response.status_code}")


