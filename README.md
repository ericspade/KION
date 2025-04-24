## Дедупликатор событий

Здравствуйте!

Здесь вы можете найти мой предварительный билд дедубликатора событий.
Билд выдерживает около 1000 RPS согласно Locust.

![image](https://github.com/user-attachments/assets/f2486876-b1ef-45ff-bf67-126e2369dec4)



## Инструкция по деплою:

1. Клонируйте этот python-проект
2. Установите Kafka, Zookeeper и Postgres как контейнеры Docker на локальной машине следующими 3мя командами:
   
      docker run -d --name kafka --network kafka-net -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -p 9092:9092 confluentinc/cp-kafka:latest
   
      docker exec kafka kafka-topics --create --topic dedup_events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   
      docker run --name pg-json -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=dbadmin -e POSTGRES_DB=kion -p 5432:5432 -d postgres:16
   
   (Тонкой настройки контейнеров не требуется)

3. Я использовал Redis для кэширования хэшей установленный как отдельная VMWare вирт. машина
   
   Образ: Ubuntu 24.10 Live Server

   Настройка сети: Bridged + Replicate physical network connection state

   Установите Ubuntu в vmware workstation и в него redis-server(порт 6379):

         sudo apt install redis-server

         sudo systemctl enable redis

         sudo systemctl start redis

         sudo apt install net-tools

      (что бы проверить работу):
         netstat -an | grep 6379

      В конфиге /etc/redis/redis.conf: измените bind на 'bind 0.0.0.0' и 'protected-mode yes' на 'protected-mode no'

      Запустите монитор событий:

         redis-cli monitor


5. Установите все нужные зависимости в python проект и запустите 3 отдельных сервиса (в 3х терминалах):
   
         python manage.py runserver
   
         python kafkacons.py
   
         uvicorn fastapi_server:app --host 0.0.0.0 --port 8001 --workers 4


API эндпоинт:

http://<ip локальной машины>:8001/api-fast/view-event


Все нужные порты:

8000 (Django)

8001 (FastAPI/uvicorn)

9092 (Kafka)

5432 (Postgres)

6379 (Redis)

Пишите мне в ТГ если возникнут проблемы с деплоем, постараюсь быстро ответить.
Деплой в конечно итоге будет в облако (AWS) как оговаривалось.
