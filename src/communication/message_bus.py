"""
MessageBus - Publish/subscribe message bus for the Mother-Baby Paradigm.

Enables decoupled, asynchronous communication between the Mother Program
and all Baby Programs without direct references.

Created by: Cherry Computer Ltd.
"""

import uuid
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..utils.logger import get_logger


@dataclass
class Message:
    """A message envelope passed through the bus."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event: str = ""
    data: Any = None
    sender: str = "unknown"
    timestamp: float = field(default_factory=time.time)
    recipient: Optional[str] = None  # None = broadcast


class MessageBus:
    """
    Thread-safe publish/subscribe message bus.

    Supports:
        - Broadcast: publish to all subscribers of an event
        - Direct: publish to a specific recipient by ID
        - Wildcard: subscribe to ALL events via the "all" channel
        - Message history: replay recent messages

    Usage:
        >>> bus = MessageBus(history_size=200)
        >>> bus.subscribe("sensor_alert", handler_fn)
        >>> bus.publish("sensor_alert", {"temp": 45.2}, sender="sensor_baby_1")
    """

    def __init__(self, history_size: int = 100):
        self.logger = get_logger("MessageBus")
        self._history_size = history_size
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._direct_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._history: List[Message] = []
        self._running = True
        self._message_count = 0

    # ─────────────────────────────────────────────
    # Subscribe
    # ─────────────────────────────────────────────

    def subscribe(self, event: str, callback: Callable) -> None:
        """
        Subscribe to a broadcast event.

        Args:
            event: Event name to listen for (use "all" for every event).
            callback: fn(event, data, sender) to invoke.
        """
        with self._lock:
            self._subscribers[event].append(callback)
        self.logger.debug(f"Subscribed to event='{event}'")

    def subscribe_direct(self, recipient_id: str, callback: Callable) -> None:
        """Subscribe to direct messages sent to a specific recipient ID."""
        with self._lock:
            self._direct_subscribers[recipient_id].append(callback)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Unsubscribe a callback from an event."""
        with self._lock:
            try:
                self._subscribers[event].remove(callback)
            except ValueError:
                pass

    # ─────────────────────────────────────────────
    # Publish
    # ─────────────────────────────────────────────

    def publish(self, event: str, data: Any = None, sender: str = "unknown") -> Message:
        """
        Broadcast an event to all subscribers.

        Args:
            event: The event name.
            data: Payload to send.
            sender: Identifier of the publisher.

        Returns:
            The Message object that was published.
        """
        msg = Message(event=event, data=data, sender=sender)
        self._record(msg)

        with self._lock:
            targets = list(self._subscribers.get(event, []))
            wildcards = list(self._subscribers.get("all", []))

        for callback in targets + wildcards:
            self._safe_call(callback, event, data, sender)

        self._message_count += 1
        return msg

    def publish_direct(self, recipient_id: str, event: str, data: Any = None, sender: str = "unknown") -> Message:
        """
        Send a direct message to a specific subscriber.

        Args:
            recipient_id: The ID of the intended recipient.
            event: Event name.
            data: Payload.
            sender: Publisher identifier.
        """
        msg = Message(event=event, data=data, sender=sender, recipient=recipient_id)
        self._record(msg)

        with self._lock:
            targets = list(self._direct_subscribers.get(recipient_id, []))

        for callback in targets:
            self._safe_call(callback, event, data, sender)

        self._message_count += 1
        return msg

    # ─────────────────────────────────────────────
    # History & Stats
    # ─────────────────────────────────────────────

    def get_history(self, event_filter: Optional[str] = None) -> List[Message]:
        """Return message history, optionally filtered by event name."""
        with self._lock:
            if event_filter:
                return [m for m in self._history if m.event == event_filter]
            return list(self._history)

    def get_stats(self) -> dict:
        return {
            "total_messages": self._message_count,
            "history_stored": len(self._history),
            "subscribed_events": list(self._subscribers.keys()),
            "direct_recipients": list(self._direct_subscribers.keys()),
        }

    def shutdown(self) -> None:
        """Shut down the message bus."""
        self._running = False
        with self._lock:
            self._subscribers.clear()
            self._direct_subscribers.clear()
        self.logger.info("MessageBus shut down.")

    # ─────────────────────────────────────────────
    # Internal
    # ─────────────────────────────────────────────

    def _record(self, msg: Message) -> None:
        with self._lock:
            self._history.append(msg)
            if len(self._history) > self._history_size:
                self._history.pop(0)

    def _safe_call(self, callback: Callable, event: str, data: Any, sender: str) -> None:
        try:
            callback(event, data, sender)
        except Exception as exc:
            self.logger.error(f"Subscriber callback error for event='{event}': {exc}")
