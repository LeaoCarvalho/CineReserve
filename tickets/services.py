from config.redis import redis_client
from django.shortcuts import get_object_or_404
from sessions.models import Session
from seats.models import Seat
from .models import Ticket
from django.db import transaction

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_seat_update(session_id, seat_id, state):
    channel_layer = get_channel_layer()

    if channel_layer is None:
        raise RuntimeError("Channel layer is not configured")

    async_to_sync(channel_layer.group_send)(
        f"session_{session_id}",
        {
            "type": "seat_update",
            "data": {
                "seat_id": seat_id,
                "state": state,
            },
        },
    )

def acquire_seat_lock(session_id, seat_id, user_id, ttl=600):
    ticket_is_taken = Ticket.objects.filter(
        session_id=session_id,
        seat_id=seat_id
    ).exists()
    if ticket_is_taken:
        return False
    key = f"seat_lock:{session_id}:{seat_id}"
    success = redis_client.set(key, user_id, nx=True, ex=ttl)

    if success:
        broadcast_seat_update(session_id, seat_id, "locked")

    return success

def get_session_seat_status(session_id):
    seats = Seat.objects.filter(
        room__session__id=session_id
    ).only("id")

    confirmed = Ticket.objects.filter(
        session_id=session_id,
    ).values_list("seat_id", flat=True)
    confirmed_seats_set = set(confirmed)

    keys = redis_client.scan_iter(f"seat_lock:{session_id}:*")
    locked_seats_set = set(
        int(key.split(":")[-1]) for key in keys
    )

    result = []

    for seat in seats:
        if seat.id in confirmed_seats_set:
            status = "taken"
        elif seat.id in locked_seats_set:
            status = "locked"
        else:
            status = "available"

        result.append({
            "seat_id": seat.id,
            "status": status
        })

    return result

def take_seat(session_id, seat_id, user_id):
    key = f"seat_lock:{session_id}:{seat_id}"
    lock_owner = redis_client.get(key)

    if not lock_owner:
        return False
    
    if lock_owner != str(user_id):
        return False
    
    try:
        with transaction.atomic():

            already_taken = Ticket.objects.filter(
                session_id=session_id,
                seat_id=seat_id
            ).exists()

            if already_taken:
                return False

            ticket = Ticket.objects.create(
                user_id=user_id,
                session_id=session_id,
                seat_id=seat_id
            )

            redis_client.delete(key)

            transaction.on_commit(lambda: 
                broadcast_seat_update(session_id, seat_id, "taken")
            )

    except Exception as e:
        return False, str(e)

    redis_client.delete(key)

    return True

