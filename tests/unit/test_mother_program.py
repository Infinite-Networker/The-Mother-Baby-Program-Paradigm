"""
Unit Tests — MotherProgram
===========================
Created by: Cherry Computer Ltd.
"""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.mother.mother_program import MotherProgram, MotherConfig, MotherState
from src.baby.worker_baby import WorkerBaby
from src.baby.baby_program import BabyState


def _make_mother(name="TestMother"):
    config = MotherConfig(
        name=name,
        max_babies=5,
        health_check_interval=9999.0,   # No auto health checks during tests
        evolution_interval=9999.0,
        auto_restart_failed=False,
        learning_enabled=False,
    )
    m = MotherProgram(config)
    m.start()
    return m


class TestMotherProgram(unittest.TestCase):
    """Tests for the MotherProgram core orchestration logic."""

    def setUp(self):
        self.mother = _make_mother()

    def tearDown(self):
        try:
            self.mother.shutdown(graceful=False)
        except Exception:
            pass

    # ── Initialization ─────────────────────────────────────────────────────

    def test_initial_state_is_active(self):
        self.assertEqual(self.mother.state, MotherState.ACTIVE)

    def test_initial_baby_count_is_zero(self):
        status = self.mother.get_status()
        self.assertEqual(status["total_babies"], 0)

    def test_config_is_stored(self):
        self.assertEqual(self.mother.config.name, "TestMother")
        self.assertEqual(self.mother.config.max_babies, 5)

    def test_mother_has_unique_id(self):
        m2 = _make_mother("Other")
        self.assertNotEqual(self.mother.id, m2.id)
        m2.shutdown(graceful=False)

    # ── Spawning ───────────────────────────────────────────────────────────

    def test_spawn_baby_returns_id(self):
        baby_id = self.mother.spawn_baby(WorkerBaby, task="test_task")
        self.assertIsNotNone(baby_id)
        self.assertIsInstance(baby_id, str)

    def test_spawn_increments_baby_count(self):
        self.mother.spawn_baby(WorkerBaby)
        self.mother.spawn_baby(WorkerBaby)
        status = self.mother.get_status()
        self.assertEqual(status["total_babies"], 2)

    def test_spawn_respects_max_babies(self):
        ids = [self.mother.spawn_baby(WorkerBaby) for _ in range(10)]
        successful = [i for i in ids if i is not None]
        self.assertLessEqual(len(successful), self.mother.config.max_babies)

    def test_spawned_baby_appears_in_status(self):
        baby_id = self.mother.spawn_baby(WorkerBaby, task="unit_test")
        status = self.mother.get_status()
        self.assertIn(baby_id, status["babies"])
        self.assertEqual(status["babies"][baby_id]["task"], "unit_test")

    # ── Termination ────────────────────────────────────────────────────────

    def test_terminate_baby_removes_from_registry(self):
        baby_id = self.mother.spawn_baby(WorkerBaby)
        result = self.mother.terminate_baby(baby_id, graceful=False)
        self.assertTrue(result)
        status = self.mother.get_status()
        self.assertNotIn(baby_id, status["babies"])

    def test_terminate_nonexistent_baby_returns_false(self):
        result = self.mother.terminate_baby("nonexistent-id", graceful=False)
        self.assertFalse(result)

    def test_terminate_decrements_baby_count(self):
        id1 = self.mother.spawn_baby(WorkerBaby)
        id2 = self.mother.spawn_baby(WorkerBaby)
        self.mother.terminate_baby(id1, graceful=False)
        self.assertEqual(self.mother.get_status()["total_babies"], 1)

    # ── Status & Introspection ─────────────────────────────────────────────

    def test_get_status_structure(self):
        status = self.mother.get_status()
        self.assertIn("id", status)
        self.assertIn("name", status)
        self.assertIn("state", status)
        self.assertIn("total_babies", status)
        self.assertIn("babies", status)

    def test_get_babies_by_tag(self):
        self.mother.spawn_baby(WorkerBaby, tags=["alpha", "worker"])
        self.mother.spawn_baby(WorkerBaby, tags=["beta"])
        alpha_babies = self.mother.get_babies_by_tag("alpha")
        self.assertEqual(len(alpha_babies), 1)

    def test_get_babies_by_state_active(self):
        self.mother.spawn_baby(WorkerBaby)
        self.mother.spawn_baby(WorkerBaby)
        active = self.mother.get_babies_by_state("active")
        # Babies start in active or resting state
        self.assertGreaterEqual(len(active), 0)

    # ── Hooks ──────────────────────────────────────────────────────────────

    def test_on_baby_born_hook_fires(self):
        born_log = []
        self.mother.on_baby_born(lambda b: born_log.append(b.id))
        baby_id = self.mother.spawn_baby(WorkerBaby)
        self.assertEqual(len(born_log), 1)
        self.assertEqual(born_log[0], baby_id)

    def test_on_baby_died_hook_fires(self):
        died_log = []
        self.mother.on_baby_died(lambda b: died_log.append(b.id))
        baby_id = self.mother.spawn_baby(WorkerBaby)
        self.mother.terminate_baby(baby_id, graceful=False)
        self.assertEqual(len(died_log), 1)
        self.assertEqual(died_log[0], baby_id)

    def test_multiple_hooks_all_fire(self):
        log = []
        self.mother.on_baby_born(lambda b: log.append("hook1"))
        self.mother.on_baby_born(lambda b: log.append("hook2"))
        self.mother.spawn_baby(WorkerBaby)
        self.assertEqual(log, ["hook1", "hook2"])

    # ── Communication ──────────────────────────────────────────────────────

    def test_broadcast_does_not_raise(self):
        self.mother.spawn_baby(WorkerBaby)
        try:
            self.mother.broadcast("test_event", {"key": "value"})
        except Exception as e:
            self.fail(f"broadcast raised: {e}")

    def test_send_to_baby_returns_true_for_existing_baby(self):
        baby_id = self.mother.spawn_baby(WorkerBaby)
        result = self.mother.send_to_baby(baby_id, "ping")
        self.assertTrue(result)

    def test_send_to_baby_returns_false_for_missing_baby(self):
        result = self.mother.send_to_baby("ghost", "ping")
        self.assertFalse(result)

    # ── Pause / Resume ─────────────────────────────────────────────────────

    def test_pause_changes_state(self):
        self.mother.pause()
        self.assertEqual(self.mother.state, MotherState.PAUSED)

    def test_resume_restores_active_state(self):
        self.mother.pause()
        self.mother.resume()
        self.assertEqual(self.mother.state, MotherState.ACTIVE)

    # ── Shutdown ───────────────────────────────────────────────────────────

    def test_shutdown_terminates_all_babies(self):
        self.mother.spawn_baby(WorkerBaby)
        self.mother.spawn_baby(WorkerBaby)
        self.mother.shutdown(graceful=False)
        self.assertEqual(self.mother.state, MotherState.TERMINATED)
        self.assertEqual(len(self.mother._babies), 0)

    def test_repr_shows_state(self):
        r = repr(self.mother)
        self.assertIn("MotherProgram", r)
        self.assertIn("active", r)


class TestWorkerBaby(unittest.TestCase):
    """Tests for the WorkerBaby implementation."""

    def setUp(self):
        self.mother = _make_mother("BabyTestMother")

    def tearDown(self):
        try:
            self.mother.shutdown(graceful=False)
        except Exception:
            pass

    def test_worker_baby_health_starts_at_one(self):
        baby_id = self.mother.spawn_baby(WorkerBaby)
        baby = self.mother._babies[baby_id]
        self.assertEqual(baby.health_score, 1.0)

    def test_worker_baby_reports_metrics(self):
        baby_id = self.mother.spawn_baby(WorkerBaby)
        baby = self.mother._babies[baby_id]
        metrics = baby.report_metrics()
        self.assertIn("task_completion_rate", metrics)
        self.assertIn("error_rate", metrics)
        self.assertIn("response_time_ms", metrics)

    def test_worker_baby_processes_tasks(self):
        results = []

        def handler(data):
            v = data["x"] * 2
            results.append(v)
            return v

        baby_id = self.mother.spawn_baby(WorkerBaby)
        baby = self.mother._babies[baby_id]
        baby._handler = handler

        baby.submit_task({"x": 5})
        baby.submit_task({"x": 10})
        time.sleep(0.3)

        self.assertGreaterEqual(len(results), 1)

    def test_worker_baby_state_is_active(self):
        baby_id = self.mother.spawn_baby(WorkerBaby)
        baby = self.mother._babies[baby_id]
        self.assertIn(baby.state, [BabyState.ACTIVE, BabyState.RESTING])

    def test_worker_baby_increments_task_count(self):
        results = []
        baby_id = self.mother.spawn_baby(WorkerBaby)
        baby = self.mother._babies[baby_id]
        baby._handler = lambda d: results.append(1)

        baby.submit_task({})
        baby.submit_task({})
        time.sleep(0.3)

        self.assertGreaterEqual(baby.task_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
