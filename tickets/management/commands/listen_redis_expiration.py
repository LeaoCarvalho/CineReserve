import redis
from django.core.management.base import BaseCommand

from tickets.services import broadcast_seat_update
from config.redis import redis_client


class Command(BaseCommand):
    help = "Listen for Redis key expiration events"

    def handle(self, *args, **options):
        pubsub = redis_client.pubsub()
        pubsub.psubscribe("__keyevent@0__:expired")

        self.stdout.write("Listening for Redis expiration events...")

        for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue

            data = message["data"]

            if isinstance(data, bytes):
                key = data.decode()
            elif isinstance(data, str):
                key = data
            else:
                # Debug unexpected case
                print(f"Unexpected data type: {type(data)} -> {data}")
                continue


            if not key.startswith("seat_lock:"):
                continue

            try:
                _, session_id, seat_id = key.split(":")
            except ValueError:
                continue


            broadcast_seat_update(
                session_id=int(session_id),
                seat_id=int(seat_id),
                state="available",
            )