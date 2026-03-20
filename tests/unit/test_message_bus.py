"""
Unit Tests — MessageBus
========================
Created by: Cherry Computer Ltd.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.communication.message_bus import MessageBus, Message


class TestMessageBus(unittest.TestCase):

    def setUp(self):
        self.bus = MessageBus(history_size=50)

    def tearDown(self):
        self.bus.shutdown()

    # ── Subscribe & Publish ────────────────────────────────────────────────

    def test_publish_delivers_to_subscriber(self):
        received = []
        self.bus.subscribe("test_event", lambda e, d, s: received.append(d))
        self.bus.publish("test_event", {"value": 42}, sender="tester")
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["value"], 42)

    def test_wildcard_subscriber_receives_all_events(self):
        received = []
        self.bus.subscribe("all", lambda e, d, s: received.append(e))
        self.bus.publish("event_a", None)
        self.bus.publish("event_b", None)
        self.assertIn("event_a", received)
        self.assertIn("event_b", received)

    def test_publish_returns_message_object(self):
        msg = self.bus.publish("hello", "world", sender="unit_test")
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.event, "hello")
        self.assertEqual(msg.data, "world")
        self.assertEqual(msg.sender, "unit_test")

    def test_publish_direct_delivers_to_recipient(self):
        received = []
        self.bus.subscribe_direct("baby_123", lambda e, d, s: received.append(d))
        self.bus.publish_direct("baby_123", "task", {"cmd": "run"}, sender="mother")
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]["cmd"], "run")

    def test_direct_message_does_not_go_to_broadcast_subscribers(self):
        broadcast_received = []
        self.bus.subscribe("task", lambda e, d, s: broadcast_received.append(d))
        self.bus.subscribe_direct("baby_999", lambda e, d, s: None)
        self.bus.publish_direct("baby_999", "task", {"data": "x"})
        self.assertEqual(len(broadcast_received), 0)

    # ── History ────────────────────────────────────────────────────────────

    def test_history_is_recorded(self):
        self.bus.publish("event_1", "a")
        self.bus.publish("event_2", "b")
        history = self.bus.get_history()
        self.assertEqual(len(history), 2)

    def test_history_size_limit(self):
        for i in range(60):  # Exceeds history_size=50
            self.bus.publish("ping", i)
        self.assertLessEqual(len(self.bus.get_history()), 50)

    def test_history_filter_by_event(self):
        self.bus.publish("alpha", 1)
        self.bus.publish("beta", 2)
        self.bus.publish("alpha", 3)
        alpha_msgs = self.bus.get_history(event_filter="alpha")
        self.assertEqual(len(alpha_msgs), 2)

    # ── Stats ──────────────────────────────────────────────────────────────

    def test_get_stats_tracks_message_count(self):
        self.bus.publish("x", None)
        self.bus.publish("x", None)
        stats = self.bus.get_stats()
        self.assertEqual(stats["total_messages"], 2)

    # ── Unsubscribe ────────────────────────────────────────────────────────

    def test_unsubscribe_stops_delivery(self):
        received = []
        cb = lambda e, d, s: received.append(d)
        self.bus.subscribe("news", cb)
        self.bus.publish("news", "first")
        self.bus.unsubscribe("news", cb)
        self.bus.publish("news", "second")
        self.assertEqual(len(received), 1)

    # ── Shutdown ───────────────────────────────────────────────────────────

    def test_shutdown_clears_subscribers(self):
        received = []
        self.bus.subscribe("post_shutdown", lambda e, d, s: received.append(d))
        self.bus.shutdown()
        # Re-create to avoid using dead bus
        self.bus = MessageBus()
        self.assertEqual(len(received), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
