"""
Supervisor - Health monitoring and auto-recovery for Baby Programs.

Created by: Cherry Computer Ltd.
"""

import threading
import time
from typing import Any
from ..utils.logger import get_logger


class Supervisor:
    """
    Monitors baby health and triggers auto-recovery via the Mother Program.

    The Supervisor runs a continuous background loop that:
        1. Asks each baby for its current health score
        2. Flags unhealthy babies
        3. Delegates recovery decisions to the MotherProgram

    Args:
        mother: Reference to the MotherProgram owning this supervisor.

    Usage:
        >>> supervisor = Supervisor(mother)
        >>> supervisor.start(interval=5.0)
    """

    def __init__(self, mother: Any):
        self.mother = mother
        self.logger = get_logger("Supervisor")
        self._running = False
        self._thread: threading.Thread = None

    def start(self, interval: float = 5.0) -> None:
        """Begin continuous health monitoring."""
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop, args=(interval,), daemon=True, name="Supervisor"
        )
        self._thread.start()
        self.logger.info(f"Supervisor started (interval={interval}s)")

    def stop(self) -> None:
        """Stop the monitoring loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10.0)
        self.logger.info("Supervisor stopped.")

    def pause(self) -> None:
        self._running = False

    def resume(self, interval: float = 5.0) -> None:
        self.start(interval)

    def _monitor_loop(self, interval: float) -> None:
        while self._running:
            self._check_all_babies()
            time.sleep(interval)

    def _check_all_babies(self) -> None:
        """Check every active baby and respond to unhealthy ones."""
        status = self.mother.get_status()
        for baby_id, baby_info in status.get("babies", {}).items():
            health = baby_info.get("health", 1.0)
            state = baby_info.get("state", "unknown")

            if state in ("crashed", "terminated"):
                if self.mother.config.auto_restart_failed:
                    self.logger.warning(
                        f"Baby {baby_id} is {state}. Auto-restarting..."
                    )
                    self.mother.restart_baby(baby_id)

            elif health < 0.3:
                self.logger.warning(
                    f"Baby {baby_id} health critical ({health:.2f}). Flagging for review."
                )
                # Optionally trigger an evaluation:
                # evaluator.evaluate(mother._babies[baby_id])
