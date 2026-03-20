"""
Lifecycle Manager - Manages health monitoring and evolution cycles.

Created by: Cherry Computer Ltd.
"""

import threading
import time
from typing import Any
from ..utils.logger import get_logger


class LifecycleManager:
    """
    Coordinates the background threads for health monitoring
    and periodic evolution cycles within the Mother Program.

    Args:
        mother: Reference to the owning MotherProgram.
    """

    def __init__(self, mother: Any):
        self.mother = mother
        self.logger = get_logger("LifecycleManager")
        self._health_thread: threading.Thread = None
        self._evolution_thread: threading.Thread = None
        self._running = False
        self._paused = False

    def start_health_monitor(self, interval: float) -> None:
        self._running = True
        self._health_thread = threading.Thread(
            target=self._health_loop, args=(interval,), daemon=True, name="HealthMonitor"
        )
        self._health_thread.start()
        self.logger.info(f"Health monitor started (interval={interval}s)")

    def start_evolution_cycle(self, interval: float) -> None:
        self._evolution_thread = threading.Thread(
            target=self._evolution_loop, args=(interval,), daemon=True, name="EvolutionCycle"
        )
        self._evolution_thread.start()
        self.logger.info(f"Evolution cycle started (interval={interval}s)")

    def stop(self) -> None:
        self._running = False
        for thread in [self._health_thread, self._evolution_thread]:
            if thread and thread.is_alive():
                thread.join(timeout=5.0)
        self.logger.info("LifecycleManager stopped.")

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def _health_loop(self, interval: float) -> None:
        while self._running:
            if not self._paused:
                try:
                    self._run_health_check()
                except Exception as exc:
                    self.logger.error(f"Health check error: {exc}")
            time.sleep(interval)

    def _evolution_loop(self, interval: float) -> None:
        while self._running:
            time.sleep(interval)
            if not self._paused and self._running:
                try:
                    self.mother._trigger_evolution()
                except Exception as exc:
                    self.logger.error(f"Evolution error: {exc}")

    def _run_health_check(self) -> None:
        status = self.mother.get_status()
        for baby_id, baby_info in status.get("babies", {}).items():
            health = baby_info.get("health", 1.0)
            state = baby_info.get("state", "unknown")
            if state == "crashed" and self.mother.config.auto_restart_failed:
                self.logger.warning(f"Baby {baby_id} crashed. Restarting...")
                self.mother.restart_baby(baby_id)
            elif health < 0.2:
                self.logger.warning(f"Baby {baby_id} critically unhealthy (health={health:.2f})")
