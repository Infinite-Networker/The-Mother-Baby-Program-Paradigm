"""
BabyProgram - Base class for all Baby Programs in the Mother-Baby Paradigm.

Baby Programs are modular, task-focused units spawned by the MotherProgram.
Each baby has a lifecycle: Born → Active → [Evolving] → [Resting] → Terminated.

Created by: Cherry Computer Ltd.
"""

import uuid
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..utils.logger import get_logger


class BabyState(Enum):
    """Lifecycle states of a Baby Program."""
    BORN       = "born"
    ACTIVE     = "active"
    PROCESSING = "processing"
    RESTING    = "resting"
    EVOLVING   = "evolving"
    CRASHED    = "crashed"
    TERMINATED = "terminated"


@dataclass
class BabyConfig:
    """Base configuration for a Baby Program."""
    name: str = "Baby"
    max_tasks: int = 1000
    rest_interval: float = 1.0      # seconds between task cycles
    evolution_enabled: bool = True
    retry_on_error: bool = True
    max_retries: int = 3


class BabyProgram(ABC):
    """
    Abstract base class for all Baby Programs.

    Subclasses must implement:
        - execute(task_data): Define the baby's core task logic.
        - report_metrics(): Return a dict of current performance metrics.

    Optional overrides:
        - on_born(): Setup when baby starts.
        - on_terminated(): Cleanup when baby stops.
        - on_message(event, data): Handle messages from the Mother / other babies.
        - evolve(): Adapt the baby's logic based on accumulated experience.

    Example:
        >>> class NumberCruncherBaby(BabyProgram):
        ...     def execute(self, task_data):
        ...         result = sum(task_data.get("numbers", []))
        ...         self.learned_data["last_sum"] = result
        ...         return result
        ...     def report_metrics(self):
        ...         return {"task_completion_rate": 1.0, "error_rate": 0.0}
    """

    def __init__(
        self,
        mother: Any,
        task: Optional[str] = None,
        config: Optional[dict] = None,
        message_bus: Optional[Any] = None,
    ):
        self.id = str(uuid.uuid4())
        self.mother = mother
        self.task = task
        self.config = BabyConfig(**(config or {})) if isinstance(config, dict) else (config or BabyConfig())
        self._message_bus = message_bus
        self.state = BabyState.BORN
        self.health_score: float = 1.0
        self.learned_data: Dict[str, Any] = {}
        self.task_count: int = 0
        self.error_count: int = 0

        self.logger = get_logger(f"Baby[{self.config.name}:{self.id[:8]}]")
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._task_queue: List[Any] = []
        self._event_handlers: Dict[str, List[Callable]] = {}

        # Subscribe to events if message bus provided
        if self._message_bus:
            self._message_bus.subscribe(self.id, self._dispatch_message)
            self._message_bus.subscribe("all", self._dispatch_message)

    # ─────────────────────────────────────────────
    # Abstract Interface
    # ─────────────────────────────────────────────

    @abstractmethod
    def execute(self, task_data: Any) -> Any:
        """Core task logic. Implement in subclasses."""
        ...

    @abstractmethod
    def report_metrics(self) -> Dict[str, float]:
        """Return a dict of current performance metrics."""
        ...

    # ─────────────────────────────────────────────
    # Lifecycle Hooks (optional overrides)
    # ─────────────────────────────────────────────

    def on_born(self) -> None:
        """Called when the baby first starts. Override for custom setup."""
        pass

    def on_terminated(self) -> None:
        """Called when the baby is terminated. Override for cleanup."""
        pass

    def on_message(self, event: str, data: Any) -> None:
        """Handle a message from the message bus. Override for custom logic."""
        pass

    def evolve(self) -> None:
        """Adapt based on learned_data. Override to implement learning."""
        pass

    # ─────────────────────────────────────────────
    # Lifecycle Control
    # ─────────────────────────────────────────────

    def start(self) -> None:
        """Start the baby's internal run loop."""
        self._running = True
        self.state = BabyState.ACTIVE
        self.on_born()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name=f"Baby-{self.id[:8]}")
        self._thread.start()
        self.logger.info(f"Baby started (task={self.task})")

    def stop(self, graceful: bool = True) -> None:
        """Stop the baby's run loop."""
        self._running = False
        if graceful and self._thread:
            self._thread.join(timeout=10.0)
        self.state = BabyState.TERMINATED
        self.on_terminated()
        self.logger.info("Baby terminated.")

    def submit_task(self, task_data: Any) -> None:
        """Queue a task for the baby to process."""
        with self._lock:
            self._task_queue.append(task_data)

    def on_event(self, event: str, callback: Callable) -> None:
        """Register an event handler."""
        self._event_handlers.setdefault(event, []).append(callback)

    # ─────────────────────────────────────────────
    # Internal Run Loop
    # ─────────────────────────────────────────────

    def _run_loop(self) -> None:
        while self._running:
            task_data = None
            with self._lock:
                if self._task_queue:
                    task_data = self._task_queue.pop(0)

            if task_data is not None:
                self._process_task(task_data)
            else:
                self.state = BabyState.RESTING
                time.sleep(self.config.rest_interval)
                if self._running:
                    self.state = BabyState.ACTIVE

    def _process_task(self, task_data: Any) -> None:
        self.state = BabyState.PROCESSING
        retries = 0
        while retries <= self.config.max_retries:
            try:
                result = self.execute(task_data)
                self.task_count += 1
                self._update_health(success=True)
                self.logger.debug(f"Task completed. result={result}")
                break
            except Exception as exc:
                retries += 1
                self.error_count += 1
                self._update_health(success=False)
                self.logger.error(f"Task error (attempt {retries}): {exc}")
                if not self.config.retry_on_error or retries > self.config.max_retries:
                    self.state = BabyState.CRASHED
                    break
        self.state = BabyState.ACTIVE

    def _update_health(self, success: bool) -> None:
        """Rolling health score update."""
        if self.task_count + self.error_count == 0:
            return
        total = self.task_count + self.error_count
        self.health_score = round(self.task_count / total, 4)

    def _dispatch_message(self, event: str, data: Any, sender: str) -> None:
        """Route an incoming message to registered handlers."""
        self.on_message(event, data)
        for handler in self._event_handlers.get(event, []):
            try:
                handler(data)
            except Exception as exc:
                self.logger.error(f"Handler error for event '{event}': {exc}")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self.id[:8]} "
            f"state={self.state.value} health={self.health_score}>"
        )
