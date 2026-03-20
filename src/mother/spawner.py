"""
Spawner - Intelligent baby spawning strategies for the Mother Program.

Provides various spawning policies: on-demand, scheduled, reactive,
and load-balanced spawning of Baby Programs.

Created by: Cherry Computer Ltd.
"""

import time
import threading
from typing import Type, Optional, List, Dict, Any
from ..baby.baby_program import BabyProgram
from ..utils.logger import get_logger


class SpawnPolicy:
    """Base class for all spawning policies."""
    def should_spawn(self, mother_status: dict) -> bool:
        raise NotImplementedError

    def get_spawn_config(self) -> dict:
        return {}


class FixedPoolPolicy(SpawnPolicy):
    """Maintain a fixed number of babies of a given type."""

    def __init__(self, baby_class: Type[BabyProgram], pool_size: int):
        self.baby_class = baby_class
        self.pool_size = pool_size

    def should_spawn(self, mother_status: dict) -> bool:
        matching = sum(
            1 for b in mother_status.get("babies", {}).values()
            if b["class"] == self.baby_class.__name__
        )
        return matching < self.pool_size


class LoadBasedPolicy(SpawnPolicy):
    """Spawn new babies when average health/load exceeds a threshold."""

    def __init__(self, baby_class: Type[BabyProgram], load_threshold: float = 0.8):
        self.baby_class = baby_class
        self.load_threshold = load_threshold

    def should_spawn(self, mother_status: dict) -> bool:
        babies = [
            b for b in mother_status.get("babies", {}).values()
            if b["class"] == self.baby_class.__name__
        ]
        if not babies:
            return True
        avg_health = sum(b["health"] for b in babies) / len(babies)
        return avg_health < self.load_threshold


class Spawner:
    """
    Manages intelligent spawning policies for the Mother Program.

    Usage:
        >>> spawner = Spawner(mother)
        >>> spawner.add_policy(FixedPoolPolicy(WorkerBaby, pool_size=5))
        >>> spawner.start_auto_spawn(interval=10.0)
    """

    def __init__(self, mother: Any):
        self.mother = mother
        self.logger = get_logger("Spawner")
        self._policies: List[SpawnPolicy] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_policy(self, policy: SpawnPolicy) -> None:
        """Add a spawning policy."""
        self._policies.append(policy)
        self.logger.info(f"Added spawn policy: {policy.__class__.__name__}")

    def evaluate_and_spawn(self) -> None:
        """Evaluate all policies and spawn babies as needed."""
        status = self.mother.get_status()
        for policy in self._policies:
            if policy.should_spawn(status):
                if isinstance(policy, (FixedPoolPolicy, LoadBasedPolicy)):
                    baby_id = self.mother.spawn_baby(
                        policy.baby_class,
                        config=policy.get_spawn_config(),
                    )
                    if baby_id:
                        self.logger.info(
                            f"Policy {policy.__class__.__name__} triggered spawn: baby_id={baby_id}"
                        )

    def start_auto_spawn(self, interval: float = 10.0) -> None:
        """Start automatic policy evaluation in the background."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, args=(interval,), daemon=True)
        self._thread.start()
        self.logger.info(f"Auto-spawn started (interval={interval}s)")

    def stop(self) -> None:
        """Stop the auto-spawn loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def _loop(self, interval: float) -> None:
        while self._running:
            self.evaluate_and_spawn()
            time.sleep(interval)
