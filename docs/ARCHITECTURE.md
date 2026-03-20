# Architecture Deep Dive

*The Mother-Baby Program Paradigm*  
*Created by **Cherry Computer Ltd.***

---

## Overview

The architecture is organized into **four layers**:

```
┌──────────────────────────────────────────┐
│          MOTHER PROGRAM LAYER            │
│  MotherProgram · Spawner · Evaluator     │
│  Supervisor · LifecycleManager           │
└─────────────────┬────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │    MESSAGE BUS     │
        │  Pub/Sub · Direct  │
        │  History · Stats   │
        └─────────┬──────────┘
                  │
┌─────────────────▼────────────────────────┐
│           BABY PROGRAM LAYER             │
│  WorkerBaby · AIBaby · SensorBaby        │
│  (+ custom BabyProgram subclasses)       │
└─────────────────┬────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │  UTILITIES LAYER   │
        │  Logger · Config   │
        └────────────────────┘
```

---

## Module Reference

### `src/mother/mother_program.py` — MotherProgram

The central orchestrator. Owns all baby references and coordinates all subsystems.

**Key Attributes:**
| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Unique UUID for this Mother instance |
| `state` | `MotherState` | Current lifecycle state |
| `config` | `MotherConfig` | Configuration object |
| `_babies` | `Dict[str, BabyProgram]` | Active baby instances |
| `_baby_registry` | `Dict[str, dict]` | Birth metadata for each baby |
| `_message_bus` | `MessageBus` | Shared communication bus |
| `_lifecycle_manager` | `LifecycleManager` | Background supervision threads |

**Key Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `start()` | None | Activate Mother and begin supervision |
| `spawn_baby(cls, task, config, tags)` | `str` or None | Spawn a new baby |
| `terminate_baby(id, graceful)` | `bool` | Stop and remove a baby |
| `restart_baby(id)` | `bool` | Stop and re-start a baby |
| `broadcast(event, data)` | None | Send to all babies |
| `send_to_baby(id, event, data)` | `bool` | Direct message to one baby |
| `get_status()` | `dict` | Full status snapshot |
| `get_babies_by_tag(tag)` | `List[BabyProgram]` | Filter babies by tag |
| `shutdown(graceful)` | None | Terminate all babies and stop |

---

### `src/mother/spawner.py` — Spawner

Policy-driven baby spawning strategies.

**Policies:**
- `FixedPoolPolicy(baby_class, pool_size)` — Maintain N babies of a type
- `LoadBasedPolicy(baby_class, load_threshold)` — Spawn when avg health < threshold

**Usage:**
```python
spawner = Spawner(mother)
spawner.add_policy(FixedPoolPolicy(WorkerBaby, pool_size=5))
spawner.start_auto_spawn(interval=10.0)
```

---

### `src/mother/evaluator.py` — Evaluator

Performance scoring and recommendation engine.

**Scoring Weights:**
| Dimension | Weight | Source |
|-----------|--------|--------|
| Task Completion Rate | 40% | `baby.report_metrics()` |
| Error Rate (inverted) | 25% | `baby.report_metrics()` |
| Response Time | 20% | Normalized against baseline |
| Resource Usage | 15% | CPU + memory |

**Grades:**
| Score | Grade | Action |
|-------|-------|--------|
| ≥ 0.90 | A | Optimal |
| ≥ 0.75 | B | Good |
| ≥ 0.60 | C | Monitor |
| ≥ 0.40 | D | Consider restart |
| < 0.40 | F | Terminate |

---

### `src/baby/baby_program.py` — BabyProgram (Abstract)

All Baby Programs extend this base class.

**Abstract Methods (must implement):**
```python
def execute(self, task_data: Any) -> Any:
    """Core task logic."""

def report_metrics(self) -> Dict[str, float]:
    """Return current performance metrics."""
```

**Optional Override Hooks:**
```python
def on_born(self) -> None: ...       # Called at startup
def on_terminated(self) -> None: ... # Called at shutdown
def on_message(self, event, data): ...  # Handle bus messages
def evolve(self) -> None: ...        # Adapt logic after evolution cycle
```

**Baby Lifecycle:**
```
BORN → ACTIVE ⇄ PROCESSING ⇄ RESTING → [EVOLVING] → [CRASHED] → TERMINATED
```

---

### `src/communication/message_bus.py` — MessageBus

Thread-safe pub/sub + direct messaging.

```python
# Broadcast to all subscribers of an event
bus.publish("sensor_alert", {"temp": 45.2}, sender="sensor_1")

# Direct message to a specific baby
bus.publish_direct("baby_uuid", "task", {"cmd": "process"}, sender="mother")

# Subscribe
bus.subscribe("sensor_alert", lambda event, data, sender: print(data))

# Replay history
history = bus.get_history(event_filter="sensor_alert")
```

---

## Extending the Framework

### Creating a Custom Baby

```python
from src.baby.baby_program import BabyProgram

class ImageProcessorBaby(BabyProgram):
    """Resizes images and publishes results."""

    def on_born(self):
        self.processed = 0
        self.logger.info("ImageProcessor ready.")

    def execute(self, task_data: dict) -> dict:
        image_path = task_data["path"]
        size = task_data.get("size", (224, 224))
        # ... perform image processing ...
        self.processed += 1
        # Notify others via message bus
        self._message_bus.publish("image_done", {
            "path": image_path, "baby_id": self.id
        }, sender=self.id)
        return {"status": "ok", "path": image_path}

    def report_metrics(self):
        total = self.task_count + self.error_count
        return {
            "task_completion_rate": self.task_count / total if total else 0.0,
            "error_rate": self.error_count / total if total else 0.0,
            "response_time_ms": 50.0,
            "memory_usage_mb": 120.0,
            "cpu_percent": 15.0,
        }
```

### Creating a Custom Spawn Policy

```python
from src.mother.spawner import SpawnPolicy

class TimeBasedPolicy(SpawnPolicy):
    """Spawn a baby only during business hours (9–17)."""

    def __init__(self, baby_class, hour_start=9, hour_end=17):
        self.baby_class = baby_class
        self.hour_start = hour_start
        self.hour_end = hour_end

    def should_spawn(self, mother_status: dict) -> bool:
        import datetime
        current_hour = datetime.datetime.now().hour
        return self.hour_start <= current_hour < self.hour_end
```

---

## Performance Considerations

| Factor | Recommendation |
|--------|---------------|
| Max babies | Keep below 100 per Mother for manageable overhead |
| Health check interval | 2–10 seconds for most use cases |
| Evolution interval | 30–300 seconds depending on learning speed needed |
| MessageBus history | 100–500 messages — larger = more memory |
| Baby rest interval | 0.1–5s depending on task arrival rate |

---

## Thread Safety

- `MotherProgram._babies` is protected by `threading.RLock()`
- `MessageBus` uses `threading.RLock()` for all subscriber lists
- Baby `_task_queue` is protected by `threading.Lock()`
- All background loops are daemon threads (auto-terminate with main process)

---

*© 2024 Cherry Computer Ltd. — MIT License*
