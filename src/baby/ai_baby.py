"""
AIBaby - An AI-powered Baby Program with built-in learning capabilities.

Maintains an internal model that adapts based on the tasks it processes.
Represents the next-generation "intelligent" baby in the paradigm.

Created by: Cherry Computer Ltd.
"""

import time
import random
import math
from typing import Any, Dict, Optional, List
from .baby_program import BabyProgram


class AIBaby(BabyProgram):
    """
    An adaptive Baby Program that learns from its task history.

    Features:
        - Confidence scoring per task type
        - Adaptive learning rate based on performance
        - Pattern memory for frequently seen tasks
        - Self-reported metrics for Mother evaluation

    Example:
        >>> ai_baby = AIBaby(mother=mother, task="classify_input")
        >>> ai_baby.start()
        >>> ai_baby.submit_task({"type": "text", "content": "Hello world"})
        >>> print(ai_baby.get_learned_patterns())
    """

    def __init__(self, mother: Any, task: Optional[str] = None,
                 config: Optional[dict] = None, message_bus: Optional[Any] = None):
        super().__init__(mother=mother, task=task, config=config, message_bus=message_bus)
        self._confidence: Dict[str, float] = {}
        self._pattern_memory: Dict[str, int] = {}
        self._learning_rate: float = 0.1
        self._response_times: List[float] = []
        self._predictions_correct: int = 0
        self._predictions_total: int = 0

    # ─────────────────────────────────────────────
    # Core Task Logic
    # ─────────────────────────────────────────────

    def execute(self, task_data: Any) -> Any:
        """Process a task using learned patterns and confidence scoring."""
        start = time.perf_counter()

        task_type = task_data.get("type", "unknown") if isinstance(task_data, dict) else str(type(task_data))
        content = task_data.get("content", task_data) if isinstance(task_data, dict) else task_data

        # Record pattern
        self._pattern_memory[task_type] = self._pattern_memory.get(task_type, 0) + 1

        # Compute confidence
        confidence = self._get_confidence(task_type)
        result = self._process_with_confidence(content, task_type, confidence)

        # Update learning
        self._update_learning(task_type, success=True)

        elapsed_ms = (time.perf_counter() - start) * 1000
        self._response_times.append(elapsed_ms)
        self._predictions_total += 1
        self._predictions_correct += 1

        self.learned_data[f"last_{task_type}"] = result
        self.logger.debug(f"AI processed task_type={task_type} confidence={confidence:.2f} result={result}")
        return result

    def _process_with_confidence(self, content: Any, task_type: str, confidence: float) -> dict:
        """Simulate AI processing — override for real model inference."""
        return {
            "task_type": task_type,
            "confidence": confidence,
            "prediction": self._simulate_prediction(content, task_type),
            "baby_id": self.id[:8],
        }

    def _simulate_prediction(self, content: Any, task_type: str) -> str:
        """Placeholder prediction — replace with real model call."""
        seen_count = self._pattern_memory.get(task_type, 1)
        if seen_count > 10:
            return f"[EXPERIENCED] Processed {task_type}: {str(content)[:50]}"
        elif seen_count > 3:
            return f"[LEARNING] Analyzing {task_type}: {str(content)[:50]}"
        else:
            return f"[NEW] Encountering {task_type} for first time: {str(content)[:50]}"

    # ─────────────────────────────────────────────
    # Learning Engine
    # ─────────────────────────────────────────────

    def _get_confidence(self, task_type: str) -> float:
        """Return current confidence score for this task type (0–1)."""
        return min(1.0, self._confidence.get(task_type, 0.1))

    def _update_learning(self, task_type: str, success: bool) -> None:
        """Update confidence and adjust learning rate."""
        current = self._confidence.get(task_type, 0.1)
        if success:
            new_confidence = current + self._learning_rate * (1.0 - current)
        else:
            new_confidence = current - self._learning_rate * current
        self._confidence[task_type] = round(max(0.0, min(1.0, new_confidence)), 4)

        # Adaptive learning rate: slow down as confidence increases
        avg_conf = sum(self._confidence.values()) / max(1, len(self._confidence))
        self._learning_rate = round(0.1 * (1.0 - avg_conf * 0.5), 4)

    def evolve(self) -> None:
        """
        Evolution: consolidate rare patterns, boost learning rate,
        and prune low-confidence task types.
        """
        before = len(self._confidence)
        # Prune task types never seen more than once with very low confidence
        self._confidence = {
            k: v for k, v in self._confidence.items()
            if self._pattern_memory.get(k, 0) > 1 or v > 0.2
        }
        pruned = before - len(self._confidence)
        # Boost learning rate slightly after evolution
        self._learning_rate = min(0.2, self._learning_rate * 1.1)
        self.logger.info(f"Evolved: pruned={pruned} task_types, lr={self._learning_rate}")

    # ─────────────────────────────────────────────
    # Reporting
    # ─────────────────────────────────────────────

    def report_metrics(self) -> Dict[str, float]:
        total = self.task_count + self.error_count
        avg_rt = (
            sum(self._response_times[-50:]) / len(self._response_times[-50:])
            if self._response_times else 0.0
        )
        return {
            "task_completion_rate": self.task_count / total if total else 0.0,
            "error_rate": self.error_count / total if total else 0.0,
            "response_time_ms": round(avg_rt, 2),
            "accuracy": self._predictions_correct / max(1, self._predictions_total),
            "avg_confidence": sum(self._confidence.values()) / max(1, len(self._confidence)),
            "memory_usage_mb": 0.0,
            "cpu_percent": 0.0,
        }

    def get_learned_patterns(self) -> dict:
        """Return all learned patterns and their confidence scores."""
        return {
            "confidence": dict(self._confidence),
            "pattern_memory": dict(self._pattern_memory),
            "learning_rate": self._learning_rate,
        }

    def on_message(self, event: str, data: Any) -> None:
        if event == "new_task":
            self.submit_task(data)
        elif event == "evolve":
            self.evolve()
        elif event == "reset_learning":
            self._confidence.clear()
            self._pattern_memory.clear()
            self.logger.info("Learning state reset via message.")
