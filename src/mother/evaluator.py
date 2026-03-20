"""
Evaluator - Performance evaluation engine for Baby Programs.

Scores babies on multiple dimensions: task completion, health,
resource usage, and response time. Drives Mother's decisions
about termination, restart, and evolution.

Created by: Cherry Computer Ltd.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import statistics
import time


@dataclass
class PerformanceMetrics:
    """Snapshot of a baby's performance metrics."""
    baby_id: str
    timestamp: float = field(default_factory=time.time)
    task_completion_rate: float = 0.0   # 0.0 – 1.0
    response_time_ms: float = 0.0
    error_rate: float = 0.0             # 0.0 – 1.0
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0
    health_score: float = 1.0           # computed composite score


@dataclass
class EvaluationResult:
    """Result of a full evaluation pass for one baby."""
    baby_id: str
    score: float                    # 0.0 – 1.0 overall score
    grade: str                      # A / B / C / D / F
    recommendations: List[str] = field(default_factory=list)
    should_terminate: bool = False
    should_restart: bool = False


class Evaluator:
    """
    Evaluates the performance of Baby Programs and recommends actions.

    Scoring weights:
        task_completion  : 40%
        error_rate       : 25%   (inverted: 1 - error_rate)
        response_time    : 20%   (normalized)
        resource_usage   : 15%

    Usage:
        >>> evaluator = Evaluator(terminate_threshold=0.2, restart_threshold=0.4)
        >>> result = evaluator.evaluate(baby)
        >>> print(result.grade, result.recommendations)
    """

    GRADE_BANDS = [
        (0.9, "A"),
        (0.75, "B"),
        (0.6, "C"),
        (0.4, "D"),
        (0.0, "F"),
    ]

    def __init__(
        self,
        terminate_threshold: float = 0.15,
        restart_threshold: float = 0.35,
        response_time_baseline_ms: float = 200.0,
    ):
        self.terminate_threshold = terminate_threshold
        self.restart_threshold = restart_threshold
        self.response_time_baseline = response_time_baseline_ms
        self._history: Dict[str, List[EvaluationResult]] = {}

    def evaluate(self, baby: Any) -> EvaluationResult:
        """
        Evaluate a Baby Program and return an EvaluationResult.

        Args:
            baby: A BabyProgram instance with metric attributes.

        Returns:
            EvaluationResult with score, grade, and recommendations.
        """
        metrics = self._gather_metrics(baby)
        score = self._compute_score(metrics)
        grade = self._assign_grade(score)
        recommendations = self._make_recommendations(metrics, score)

        result = EvaluationResult(
            baby_id=baby.id,
            score=round(score, 4),
            grade=grade,
            recommendations=recommendations,
            should_terminate=score < self.terminate_threshold,
            should_restart=self.terminate_threshold <= score < self.restart_threshold,
        )

        self._history.setdefault(baby.id, []).append(result)
        return result

    def _gather_metrics(self, baby: Any) -> PerformanceMetrics:
        """Pull metrics from the baby's internal reporting API."""
        metrics_data = baby.report_metrics() if hasattr(baby, "report_metrics") else {}
        return PerformanceMetrics(
            baby_id=baby.id,
            task_completion_rate=metrics_data.get("task_completion_rate", 0.5),
            response_time_ms=metrics_data.get("response_time_ms", 100.0),
            error_rate=metrics_data.get("error_rate", 0.0),
            memory_usage_mb=metrics_data.get("memory_usage_mb", 50.0),
            cpu_percent=metrics_data.get("cpu_percent", 10.0),
            health_score=getattr(baby, "health_score", 1.0),
        )

    def _compute_score(self, m: PerformanceMetrics) -> float:
        """Weighted composite score computation."""
        completion_score = m.task_completion_rate                       # 0–1
        error_score = 1.0 - m.error_rate                               # 0–1
        rt_score = max(0.0, 1.0 - m.response_time_ms / (self.response_time_baseline * 5))
        resource_score = max(0.0, 1.0 - (m.cpu_percent / 100.0) * 0.5 - (m.memory_usage_mb / 512.0) * 0.5)

        return (
            0.40 * completion_score
            + 0.25 * error_score
            + 0.20 * rt_score
            + 0.15 * resource_score
        )

    def _assign_grade(self, score: float) -> str:
        for threshold, grade in self.GRADE_BANDS:
            if score >= threshold:
                return grade
        return "F"

    def _make_recommendations(self, m: PerformanceMetrics, score: float) -> List[str]:
        recs = []
        if m.error_rate > 0.3:
            recs.append("High error rate detected — review task logic or input validation.")
        if m.response_time_ms > self.response_time_baseline * 3:
            recs.append("Response time degraded — consider splitting workload across more babies.")
        if m.cpu_percent > 80:
            recs.append("CPU usage critical — offload work or increase pool size.")
        if m.memory_usage_mb > 400:
            recs.append("Memory near limit — check for leaks or large object retention.")
        if m.task_completion_rate < 0.5:
            recs.append("Low task completion — ensure baby is receiving correct inputs.")
        if not recs and score >= 0.9:
            recs.append("Performing optimally — no action required.")
        return recs

    def get_history(self, baby_id: str) -> List[EvaluationResult]:
        """Return evaluation history for a specific baby."""
        return self._history.get(baby_id, [])

    def trending_score(self, baby_id: str, window: int = 5) -> Optional[float]:
        """Compute average score over the last N evaluations."""
        history = self.get_history(baby_id)[-window:]
        if not history:
            return None
        return statistics.mean(r.score for r in history)
