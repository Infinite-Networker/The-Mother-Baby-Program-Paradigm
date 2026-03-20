"""
MotherProgram - Core intelligent orchestrator in the Mother-Baby Paradigm.

The MotherProgram acts as the central brain: it spawns Baby Programs,
monitors their health, coordinates their communication, and evolves
the system over time.

Created by: Cherry Computer Ltd.
"""

import uuid
import logging
import threading
import time
from typing import Dict, List, Optional, Callable, Any, Type
from dataclasses import dataclass, field
from enum import Enum

from ..baby.baby_program import BabyProgram
from ..lifecycle.lifecycle_manager import LifecycleManager
from ..communication.message_bus import MessageBus
from ..utils.logger import get_logger


class MotherState(Enum):
    """Lifecycle states of the Mother Program."""
    INITIALIZING = "initializing"
    ACTIVE       = "active"
    PAUSED       = "paused"
    EVOLVING     = "evolving"
    SHUTTING_DOWN = "shutting_down"
    TERMINATED   = "terminated"


@dataclass
class MotherConfig:
    """Configuration for the Mother Program."""
    name: str = "MotherProgram"
    max_babies: int = 50
    health_check_interval: float = 5.0      # seconds
    evolution_interval: float = 60.0        # seconds
    auto_restart_failed: bool = True
    learning_enabled: bool = True
    log_level: str = "INFO"


class MotherProgram:
    """
    The central intelligence orchestrator of the Mother-Baby Paradigm.

    Responsibilities:
        - Spawning Baby Programs with specific roles/tasks
        - Monitoring baby health and performance
        - Facilitating inter-baby communication
        - Terminating or restarting babies as needed
        - Evolving the ecosystem over time

    Example:
        >>> mother = MotherProgram(MotherConfig(name="MyMother", max_babies=10))
        >>> mother.start()
        >>> baby_id = mother.spawn_baby(DataProcessorBaby, task="process_csv")
        >>> mother.broadcast("start_processing")
        >>> mother.shutdown()
    """

    def __init__(self, config: Optional[MotherConfig] = None):
        self.config = config or MotherConfig()
        self.id = str(uuid.uuid4())
        self.state = MotherState.INITIALIZING
        self.logger = get_logger(self.config.name)

        # Core subsystems
        self._message_bus = MessageBus()
        self._lifecycle_manager = LifecycleManager(self)
        self._babies: Dict[str, BabyProgram] = {}
        self._baby_registry: Dict[str, dict] = {}
        self._performance_log: List[dict] = []
        self._lock = threading.RLock()

        # Hooks
        self._on_baby_born: List[Callable] = []
        self._on_baby_died: List[Callable] = []
        self._on_evolution: List[Callable] = []

        self.logger.info(f"[{self.config.name}] Mother Program initialized (id={self.id})")

    # ─────────────────────────────────────────────
    # Lifecycle Control
    # ─────────────────────────────────────────────

    def start(self) -> None:
        """Activate the Mother Program and begin supervision loops."""
        self.state = MotherState.ACTIVE
        self._lifecycle_manager.start_health_monitor(self.config.health_check_interval)
        if self.config.learning_enabled:
            self._lifecycle_manager.start_evolution_cycle(self.config.evolution_interval)
        self.logger.info(f"[{self.config.name}] Mother Program is now ACTIVE.")

    def pause(self) -> None:
        """Pause all supervision activities."""
        self.state = MotherState.PAUSED
        self._lifecycle_manager.pause()
        self.logger.info(f"[{self.config.name}] Mother Program PAUSED.")

    def resume(self) -> None:
        """Resume supervision from a paused state."""
        self.state = MotherState.ACTIVE
        self._lifecycle_manager.resume()
        self.logger.info(f"[{self.config.name}] Mother Program RESUMED.")

    def shutdown(self, graceful: bool = True) -> None:
        """
        Gracefully shut down the Mother Program and all its babies.

        Args:
            graceful: If True, waits for babies to complete their current task.
        """
        self.state = MotherState.SHUTTING_DOWN
        self.logger.info(f"[{self.config.name}] Initiating shutdown (graceful={graceful})...")
        for baby_id in list(self._babies.keys()):
            self.terminate_baby(baby_id, graceful=graceful)
        self._lifecycle_manager.stop()
        self._message_bus.shutdown()
        self.state = MotherState.TERMINATED
        self.logger.info(f"[{self.config.name}] Mother Program TERMINATED.")

    # ─────────────────────────────────────────────
    # Baby Spawning & Termination
    # ─────────────────────────────────────────────

    def spawn_baby(
        self,
        baby_class: Type[BabyProgram],
        task: Optional[str] = None,
        config: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Spawn a new Baby Program.

        Args:
            baby_class: The BabyProgram subclass to instantiate.
            task: A task description for the baby.
            config: Optional configuration dict for the baby.
            tags: Metadata tags for grouping / querying babies.

        Returns:
            The baby's unique ID, or None if max capacity is reached.
        """
        with self._lock:
            if len(self._babies) >= self.config.max_babies:
                self.logger.warning(f"[{self.config.name}] Max baby limit ({self.config.max_babies}) reached.")
                return None

            baby = baby_class(
                mother=self,
                task=task,
                config=config or {},
                message_bus=self._message_bus,
            )
            self._babies[baby.id] = baby
            self._baby_registry[baby.id] = {
                "class": baby_class.__name__,
                "task": task,
                "tags": tags or [],
                "born_at": time.time(),
                "restarts": 0,
            }

            baby.start()
            self.logger.info(f"[{self.config.name}] Spawned baby '{baby_class.__name__}' (id={baby.id}, task={task})")

            for hook in self._on_baby_born:
                try:
                    hook(baby)
                except Exception as exc:
                    self.logger.error(f"Hook error on baby born: {exc}")

            return baby.id

    def terminate_baby(self, baby_id: str, graceful: bool = True) -> bool:
        """
        Terminate a specific Baby Program.

        Args:
            baby_id: The ID of the baby to terminate.
            graceful: Whether to allow the baby to finish its current task.

        Returns:
            True if terminated successfully, False otherwise.
        """
        with self._lock:
            baby = self._babies.pop(baby_id, None)
            if not baby:
                self.logger.warning(f"[{self.config.name}] Baby {baby_id} not found.")
                return False

            baby.stop(graceful=graceful)
            self.logger.info(f"[{self.config.name}] Terminated baby {baby_id}.")

            for hook in self._on_baby_died:
                try:
                    hook(baby)
                except Exception as exc:
                    self.logger.error(f"Hook error on baby died: {exc}")

            return True

    def restart_baby(self, baby_id: str) -> bool:
        """Restart a Baby Program by terminating and re-spawning it."""
        with self._lock:
            registry = self._baby_registry.get(baby_id)
            if not registry:
                return False
            baby = self._babies.get(baby_id)
            if baby:
                baby.stop(graceful=False)
                baby.start()
                registry["restarts"] += 1
                self.logger.info(f"[{self.config.name}] Restarted baby {baby_id} (restart #{registry['restarts']}).")
                return True
            return False

    # ─────────────────────────────────────────────
    # Communication
    # ─────────────────────────────────────────────

    def broadcast(self, event: str, data: Any = None) -> None:
        """Broadcast an event to all active Baby Programs."""
        self._message_bus.publish(event, data, sender="mother")
        self.logger.debug(f"[{self.config.name}] Broadcast event='{event}'")

    def send_to_baby(self, baby_id: str, event: str, data: Any = None) -> bool:
        """Send a direct message to a specific Baby Program."""
        baby = self._babies.get(baby_id)
        if not baby:
            return False
        self._message_bus.publish_direct(baby_id, event, data, sender="mother")
        return True

    # ─────────────────────────────────────────────
    # Introspection & Status
    # ─────────────────────────────────────────────

    def get_status(self) -> dict:
        """Return a full status snapshot of the Mother Program."""
        with self._lock:
            return {
                "id": self.id,
                "name": self.config.name,
                "state": self.state.value,
                "total_babies": len(self._babies),
                "max_babies": self.config.max_babies,
                "babies": {
                    bid: {
                        "class": self._baby_registry[bid]["class"],
                        "task": self._baby_registry[bid]["task"],
                        "state": b.state.value,
                        "health": b.health_score,
                        "restarts": self._baby_registry[bid]["restarts"],
                    }
                    for bid, b in self._babies.items()
                },
            }

    def get_babies_by_tag(self, tag: str) -> List[BabyProgram]:
        """Retrieve all babies matching a given tag."""
        return [
            self._babies[bid]
            for bid, meta in self._baby_registry.items()
            if tag in meta.get("tags", []) and bid in self._babies
        ]

    def get_babies_by_state(self, state: str) -> List[BabyProgram]:
        """Retrieve all babies in a given state."""
        return [b for b in self._babies.values() if b.state.value == state]

    # ─────────────────────────────────────────────
    # Hook Registration
    # ─────────────────────────────────────────────

    def on_baby_born(self, callback: Callable) -> None:
        """Register a callback that fires whenever a new baby is spawned."""
        self._on_baby_born.append(callback)

    def on_baby_died(self, callback: Callable) -> None:
        """Register a callback that fires whenever a baby is terminated."""
        self._on_baby_died.append(callback)

    def on_evolution(self, callback: Callable) -> None:
        """Register a callback that fires during each evolution cycle."""
        self._on_evolution.append(callback)

    def _trigger_evolution(self) -> None:
        """Internal: run evolution callbacks and log performance."""
        self.state = MotherState.EVOLVING
        snapshot = self.get_status()
        self._performance_log.append(snapshot)
        for hook in self._on_evolution:
            try:
                hook(snapshot)
            except Exception as exc:
                self.logger.error(f"Hook error during evolution: {exc}")
        self.state = MotherState.ACTIVE
        self.logger.info(f"[{self.config.name}] Evolution cycle complete.")

    def __repr__(self) -> str:
        return (
            f"<MotherProgram name={self.config.name!r} "
            f"state={self.state.value} babies={len(self._babies)}>"
        )
