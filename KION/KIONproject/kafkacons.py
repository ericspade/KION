import json
import os
import traceback
from datetime import datetime
from kafka import KafkaConsumer
import psycopg2

# Kafka config
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "dedup_events")
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVERS,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="ydb-writer-group"
)


def write_postgres(payload):
    data = payload["data"]
    dedupe_key = payload["dedupe_key"]
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "kion"),
            user=os.getenv("POSTGRES_USER", "admin"),
            password=os.getenv("POSTGRES_PASSWORD", "dbadmin"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        print("DB connected")
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO dedupe_events (
    platform, event_name, profile_age, user_agent, screen, event_datetime_str,
  event_datetime, event_date, auth_method, auth_type, request_id, referer,
  subscription_name, subscription_id, deeplink, payment_type, transaction_id,
  purchase_option, content_type, content_gid, content_name, content_id,
  promocode, promocode_code, quality, play_url, channel_name, channel_id,
  channel_gid, cause, button_id, button_text, feedback_text, experiments,
  season, episode, discount_items_ids, discount_items_names, content_provider,
  story_type, "userId", playtime_ms, duration, client_id, discount, is_trial,
  price, dt_add, url_user_event, event_receive_timestamp, event_receive_dt_str,
  shelf_name, shelf_index, card_index, error_message, platform_useragent,
  product_id, dl, fp, dr, mc, r, sc, sid, sr, title, ts, wr, cid, uid, ll, av,
  os, mnf, mdl, os_family, os_version, is_mobile, is_pc, is_tablet,
  is_touch_capable, client_id_body, client_id_query, time, field_id,
  field_action, search_films, recommended_films, event_datetime_msc,
  user_device_is_tv, input_type, product_names, product_ids, prices,
  auth_status_list, "isJunior", waterbase_device_id, error_url, error_severity,
  error_category, error_code, os_build, banner_type, banner_id, banner_gid,
  kion_session_id, popup_name, popup_action, app_version, downloaded, osv, dt,
  dm, lc, event_source, device_id, debug, host, path, request_type, code,
  message, field_text, card_gid, "current_time", card_id, card_type, card_name,
  uuid, term, playing_mode, inserted_dt, build_model, build_manufacturer,
  extra_field, trouble_report, playback_speed
)
VALUES (
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s, %s, %s
)
        """,
                    (
                        data.get("platform"),
                        data.get("event_name"),
                        data.get("profile_age"),
                        data.get("user_agent"),
                        data.get("screen"),
                        data.get("event_datetime_str"),
                        data.get("event_datetime"),
                        data.get("event_date"),
                        data.get("auth_method"),
                        data.get("auth_type"),
                        data.get("request_id"),
                        data.get("referer"),
                        data.get("subscription_name"),
                        data.get("subscription_id"),
                        data.get("deeplink"),
                        data.get("payment_type"),
                        data.get("transaction_id"),
                        data.get("purchase_option"),
                        data.get("content_type"),
                        data.get("content_gid"),
                        data.get("content_name"),
                        data.get("content_id"),
                        data.get("promocode"),
                        data.get("promocode_code"),
                        data.get("quality"),
                        data.get("play_url"),
                        data.get("channel_name"),
                        data.get("channel_id"),
                        data.get("channel_gid"),
                        data.get("cause"),
                        data.get("button_id"),
                        data.get("button_text"),
                        data.get("feedback_text"),
                        data.get("experiments"),
                        data.get("season"),
                        data.get("episode"),
                        data.get("discount_items_ids"),
                        data.get("discount_items_names"),
                        data.get("content_provider"),
                        data.get("story_type"),
                        data.get("userId"),
                        data.get("playtime_ms"),
                        data.get("duration"),
                        data.get("client_id"),
                        data.get("discount"),
                        data.get("is_trial"),
                        data.get("price"),
                        data.get("dt_add"),
                        data.get("url_user_event"),
                        data.get("event_receive_timestamp"),
                        data.get("event_receive_dt_str"),
                        data.get("shelf_name"),
                        data.get("shelf_index"),
                        data.get("card_index"),
                        data.get("error_message"),
                        data.get("platform_useragent"),
                        data.get("product_id"),
                        data.get("dl"),
                        data.get("fp"),
                        data.get("dr"),
                        data.get("mc"),
                        data.get("r"),
                        data.get("sc"),
                        data.get("sid"),
                        data.get("sr"),
                        data.get("title"),
                        data.get("ts"),
                        data.get("wr"),
                        data.get("cid"),
                        data.get("uid"),
                        data.get("ll"),
                        data.get("av"),
                        data.get("os"),
                        data.get("mnf"),
                        data.get("mdl"),
                        data.get("os_family"),
                        data.get("os_version"),
                        data.get("is_mobile"),
                        data.get("is_pc"),
                        data.get("is_tablet"),
                        data.get("is_touch_capable"),
                        data.get("client_id_body"),
                        data.get("client_id_query"),
                        data.get("time"),
                        data.get("field_id"),
                        data.get("field_action"),
                        data.get("search_films"),
                        data.get("recommended_films"),
                        data.get("event_datetime_msc"),
                        data.get("user_device_is_tv"),
                        data.get("input_type"),
                        data.get("product_names"),
                        data.get("product_ids"),
                        data.get("prices"),
                        data.get("auth_status_list"),
                        data.get("isJunior"),
                        data.get("waterbase_device_id"),
                        data.get("error_url"),
                        data.get("error_severity"),
                        data.get("error_category"),
                        data.get("error_code"),
                        data.get("os_build"),
                        data.get("banner_type"),
                        data.get("banner_id"),
                        data.get("banner_gid"),
                        data.get("kion_session_id"),
                        data.get("popup_name"),
                        data.get("popup_action"),
                        data.get("app_version"),
                        data.get("downloaded"),
                        data.get("osv"),
                        data.get("dt"),
                        data.get("dm"),
                        data.get("lc"),
                        data.get("event_source"),
                        data.get("device_id"),
                        data.get("debug"),
                        data.get("host"),
                        data.get("path"),
                        data.get("request_type"),
                        data.get("code"),
                        data.get("message"),
                        data.get("field_text"),
                        data.get("card_gid"),
                        data.get("current_time"),
                        data.get("card_id"),
                        data.get("card_type"),
                        data.get("card_name"),
                        data.get("uuid"),
                        data.get("term"),
                        data.get("playing_mode"),
                        data.get("inserted_dt"),
                        data.get("build_model"),
                        data.get("build_manufacturer"),
                        data.get("extra_field"),
                        data.get("trouble_report"),
                        data.get("playback_speed")
                    ))
        conn.commit()
        print("Записано в основную БД")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка записи в БД: {e}")
        traceback.print_exc()


print("[Kafka] В ожидании")
for message in consumer:
    try:
        payload = message.value
        print(f"[Kafka] Обработка события: {payload['dedupe_key']}")
        write_postgres(payload)
    except Exception as e:
        print(f"[Kafka] Ошибка очереди: {e}")
