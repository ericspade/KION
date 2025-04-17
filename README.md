Здравствуйте!

Здесь вы можете найти мой предварительный билд дедубликатора событий.
Билд выдерживает чуть меньше 1000 RPS согласно Locust.

![LocustTEST](https://github.com/user-attachments/assets/1cd8bcf9-d450-48e2-bedc-c25e8326598b)


Инструкция по деплою:

1) Клонируйте этот python-проект
2) Установите Kafka, Zookeeper Postgres как контейнеры Docker на локальной машине следующими 3мя командами:
   docker run -d --name kafka --network kafka-net -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 -p 9092:9092 confluentinc/cp-kafka:latest
   
   docker exec kafka kafka-topics --create --topic dedup_events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   
   docker run --name pg-json -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=dbadmin -e POSTGRES_DB=kion -p 5432:5432 -d postgres:16
   (Тонкой настройки контейнеров не требуется)

4) Я использовал Redis для кэширования хэшей установленный как отдельная VMWare вирт. машина
Образ: Ubuntu 24.10 Live Server
Настройка сети: Bridged + Replicate physical network connection state

Установите Ubuntu в vmware workstation и в него redis-server(порт 6379):
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
sudo apt install net-tools
(что бы проверить работу): netstat -an | grep 6379

В конфиге /etc/redis/redis.conf: измените bind на 'bind 0.0.0.0' и 'protected-mode yes' на 'protected-mode no'

Запустите монитор событий:
redis-cli monitor


4) Установите все нужные зависимости в python проект и запустите 3 отдельных сервиса (в 3х терминалах):
   python manage.py runserver
   python kafkacons.py
   uvicorn fastapi_server:app --host 0.0.0.0 --port 8001 --workers 4
