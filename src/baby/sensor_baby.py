"""
SensorBaby - A Baby Program designed for continuous data monitoring & streaming.

Reads from data sources (simulated sensors, APIs, streams) and forwards
processed readings to the Mother Program or peer babies.

Created by: Cherry Computer Ltd.
"""

import time
import random
import threading
from typing import Any, Callable, Dict, List, Optional
from .baby_program import BabyProgram


class SensorBaby(BabyProgram):
    """
    Continuously samples a data source and emits readings.

    Args:
        sensor_fn: A callable returning the current sensor reading.
        emit_interval: Seconds between readings.
        alert_threshold: If reading exceeds this, alert the mother.

    Example:
        >>> def temp_sensor():
        ...     return random.uniform(18.0, 45.0)
        >>> sensor = SensorBaby(mother=mother, sensor_fn=temp_sensor,
        ...                      emit_interval=2.0, alert_threshold=40.0)
        >>> sensor.start()
    """

    def __init__(
        self,
        mother: Any,
        task: Optional[str] = None,
        config: Optional[dict] = None,
        message_bus: Optional[Any] = None,
        sensor_fn: Optional[Callable] = None,
        emit_interval: float = 2.0,
        alert_threshold: Optional[float] = None,
    ):
        super().__init__(mother=mother, task=task, config=config, message_bus=message_bus)
        self._sensor_fn = sensor_fn or self._default_sensor
        self._emit_interval = emit_interval
        self._alert_threshold = alert_threshold
        self._readings: List[float] = []
        self._alert_count: int = 0
        self._response_times: List[float] = []

    def on_born(self) -> None:
        """Start the autonomous sensor sampling loop."""
        self._sensor_thread = threading.Thread(
            target=self._sample_loop, daemon=True, name=f"Sensor-{self.id[:8]}"
        )
        self._sensor_thread.start()
        self.logger.info(f"Sensor loop started (interval={self._emit_interval}s)")

    def execute(self, task_data: Any) -> Any:
        """Process a manually submitted task (secondary pathway)."""
        return self._sensor_fn()

    def _sample_loop(self) -> None:
        while self._running:
            t0 = time.perf_counter()
            try:
                reading = self._sensor_fn()
                self._readings.append(reading)
                self.task_count += 1
                elapsed_ms = (time.perf_counter() - t0) * 1000
                self._response_times.append(elapsed_ms)
                self._update_health(success=True)

                # Alert logic
                if self._alert_threshold is not None and reading > self._alert_threshold:
                    self._alert_count += 1
                    if self._message_bus:
                        self._message_bus.publish(
                            "sensor_alert",
                            {"baby_id": self.id, "reading": reading, "threshold": self._alert_threshold},
                            sender=self.id,
                        )
                    self.logger.warning(
                        f"ALERT: reading={reading:.2f} exceeds threshold={self._alert_threshold}"
                    )

                # Publish normal reading
                if self._message_bus:
                    self._message_bus.publish(
                        "sensor_reading",
                        {"baby_id": self.id, "reading": reading, "timestamp": time.time()},
                        sender=self.id,
                    )
            except Exception as exc:
                self.error_count += 1
                self._update_health(success=False)
                self.logger.error(f"Sensor error: {exc}")

            time.sleep(self._emit_interval)

    def _default_sensor(self) -> float:
        """Default: simulated temperature sensor."""
        return round(random.uniform(20.0, 35.0), 2)

    def get_readings(self) -> List[float]:
        return list(self._readings[-100:])

    def get_average(self) -> Optional[float]:
        if not self._readings:
            return None
        return round(sum(self._readings) / len(self._readings), 4)

    def report_metrics(self) -> Dict[str, float]:
        total = self.task_count + self.error_count
        return {
            "task_completion_rate": self.task_count / total if total else 0.0,
            "error_rate": self.error_count / total if total else 0.0,
            "response_time_ms": (
                sum(self._response_times[-50:]) / len(self._response_times[-50:])
                if self._response_times else 0.0
            ),
            "alert_count": float(self._alert_count),
            "avg_reading": self.get_average() or 0.0,
            "memory_usage_mb": 0.0,
            "cpu_percent": 0.0,
        }
