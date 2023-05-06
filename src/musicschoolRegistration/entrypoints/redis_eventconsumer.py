import json
import logging
import redis

from musicschoolRegistration import bootstrap, config
from musicschoolRegistration.domain import commands

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def main():
    logger.info("Redis pubsub starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("musicLesson_registration")

    for m in pubsub.listen():
        handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(m, bus):
    logger.info("handling %s", m)
    data = json.loads(m["data"])
    cmd = commands.UpdateService(lesson_name=data["lesson_name"], price=data["price"])
    bus.handle(cmd)


if __name__ == "__main__":
    main()
