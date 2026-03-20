"""
WorkerBaby - A general-purpose task-executing Baby Program.

Designed for CPU-bound batch processing tasks such as data
transformation, file processing, and computation pipelines.

Created by: Cherry Computer Ltd.
"""

import time
from typing import Any, Dict, Callable, Optional
from .baby_program import BabyProgram, BabyConfig


class WorkerBaby(BabyProgram):
    """
    A versatile Worker Baby that accepts a callable handler as its task logic.

    Args:
        handler: A function to execute for each task item.
        config: BabyConfig overrides.

    Example:
        >>> def double(data):
        ...     return data["value"] * 2
        >>> baby = WorkerBaby(mother=mother, config={"name": "Doubler"}, handler=double)
        >>> baby.start()
        >>> baby.submit_task({"value": 21})
    """

    def __init__(self, mother: Any, task: Optional[str] = None, config: Optional[dict] = None,
                 message_bus: Optional[Any] = None, handler: Optional[Callable] = None):
        super().__init__(mother=mother, task=task, config=config, message_bus=message_bus)
        self._handler = handler or self._default_handler
        self._results: list = []
        self._response_times: list = []

    def execute(self, task_data: Any) -> Any:
        start = time.perf_counter()
        result = self._handler(task_data)
        elapsed_ms = (time.perf_counter() - start) * 1000
        self._results.append(result)
        self._response_times.append(elapsed_ms)
        return result

    def report_metrics(self) -> Dict[str, float]:
        total = self.task_count + self.error_count
        return {
            "task_completion_rate": self.task_count / total if total else 0.0,
            "error_rate": self.error_count / total if total else 0.0,
            "response_time_ms": (
                sum(self._response_times[-50:]) / len(self._response_times[-50:])
                if self._response_times else 0.0
            ),
            "memory_usage_mb": 0.0,
            "cpu_percent": 0.0,
        }

    def get_results(self) -> list:
        """Return all results produced so far."""
        return list(self._results)

    def _default_handler(self, data: Any) -> Any:
        self.logger.info(f"Processing: {data}")
        return data

    def on_message(self, event: str, data: Any) -> None:
        if event == "new_task":
            self.submit_task(data)
        elif event == "clear_results":
            self._results.clear()
