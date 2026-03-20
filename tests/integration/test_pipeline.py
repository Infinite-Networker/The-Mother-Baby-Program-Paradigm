"""
Integration Test — Full Mother-Baby Pipeline
=============================================
Tests the complete lifecycle of a Mother-Baby system.

Created by: Cherry Computer Ltd.
"""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.mother.mother_program import MotherProgram, MotherConfig, MotherState
from src.baby.worker_baby import WorkerBaby
from src.baby.ai_baby import AIBaby


class TestFullPipeline(unittest.TestCase):
    """Integration tests: full spawning, task flow, and shutdown cycle."""

    def setUp(self):
        config = MotherConfig(
            name="IntegrationMother",
            max_babies=10,
            health_check_interval=100.0,
            evolution_interval=1000.0,
            learning_enabled=False,
        )
        self.mother = MotherProgram(config)
        self.mother.start()

    def tearDown(self):
        if self.mother.state != MotherState.TERMINATED:
            self.mother.shutdown(graceful=False)

    def test_full_worker_pipeline(self):
        """Spawn → submit tasks → collect results → shutdown."""
        outputs = []

        def handler(data):
            val = data.get("n", 0) * 3
            outputs.append(val)
            return val

        baby_id = self.mother.spawn_baby(WorkerBaby, task="multiply_by_3")
        baby = self.mother._babies[baby_id]
        baby._handler = handler

        for i in range(1, 6):
            baby.submit_task({"n": i})

        time.sleep(1.0)

        self.assertEqual(sorted(outputs), [3, 6, 9, 12, 15])

    def test_multiple_babies_parallel(self):
        """Spawn multiple babies and verify they all process concurrently."""
        counters = {"count": 0}

        def counter_handler(data):
            counters["count"] += 1
            return counters["count"]

        ids = [self.mother.spawn_baby(WorkerBaby) for _ in range(3)]
        for baby_id in ids:
            self.mother._babies[baby_id]._handler = counter_handler
            for _ in range(5):
                self.mother._babies[baby_id].submit_task({})

        time.sleep(1.5)
        self.assertEqual(counters["count"], 15)

    def test_ai_baby_learns_from_tasks(self):
        """AIBaby should accumulate pattern memory over tasks."""
        ai_id = self.mother.spawn_baby(AIBaby, task="classify")
        ai_baby = self.mother._babies[ai_id]

        for i in range(15):
            ai_baby.submit_task({"type": "temperature", "content": 22.5 + i})

        time.sleep(2.0)

        patterns = ai_baby.get_learned_patterns()
        self.assertIn("temperature", patterns["pattern_memory"])
        self.assertGreater(patterns["pattern_memory"]["temperature"], 0)
        self.assertIn("temperature", patterns["confidence"])

    def test_broadcast_reaches_all_babies(self):
        """Broadcast from Mother should be received by all babies."""
        received_count = {"n": 0}

        class CountingBaby(WorkerBaby):
            def on_message(self, event, data):
                if event == "ping":
                    received_count["n"] += 1

        baby_ids = [self.mother.spawn_baby(CountingBaby) for _ in range(3)]
        time.sleep(0.2)
        self.mother.broadcast("ping", {"msg": "hello"})
        time.sleep(0.3)
        self.assertEqual(received_count["n"], 3)

    def test_restart_baby_increments_counter(self):
        """Restarting a baby should increment its restart counter."""
        baby_id = self.mother.spawn_baby(WorkerBaby)
        self.mother.restart_baby(baby_id)
        registry = self.mother._baby_registry.get(baby_id, {})
        self.assertEqual(registry.get("restarts", 0), 1)

    def test_full_shutdown_terminates_all(self):
        """After shutdown, all babies should be gone."""
        for _ in range(4):
            self.mother.spawn_baby(WorkerBaby)
        self.mother.shutdown(graceful=False)
        self.assertEqual(len(self.mother._babies), 0)
        self.assertEqual(self.mother.state, MotherState.TERMINATED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
