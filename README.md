<div align="center">

<img src="https://github.com/Infinite-Networker/The-Mother-Baby-Program-Paradigm/blob/8b0dc65cd8b76612d19f39faecdb612be2dcb5ad/.img" 
width="320"/>


# 🍒 The Mother-Baby Program Paradigm



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Created By](https://img.shields.io/badge/Created%20By-Cherry%20Computer%20Ltd.-red.svg)](#-created-by-cherry-computer-ltd)
[![Architecture](https://img.shields.io/badge/Architecture-Bio--Inspired-ff69b4.svg)](#-architecture)

**A life-inspired, modular software architecture framework where intelligent Mother Programs  
spawn, nurture, and coordinate specialized Baby Programs to create adaptive,  
self-managing software ecosystems.**

*Created and maintained by **Cherry Computer Ltd.***

</div>

---

## 🌟 Overview

The **Mother-Baby Program Paradigm** draws inspiration from biological relationships to create software systems that evolve like life itself. This framework separates software into two dynamic layers:

- 🧠 **Mother Program** — The intelligent core/controller that spawns, manages, evolves, and learns from Baby Programs
- 👶 **Baby Programs** — Modular, specialized units capable of learning, adapting, and self-managing for specific tasks

Together they form an **ecosystem** — not just a system.

---

## 🏢 Created by Cherry Computer Ltd.

> This repository, framework, and all associated concepts, code, documentation, and designs were created by **Cherry Computer Ltd.**

**Cherry Computer Ltd.** is a technology company pioneering bio-inspired software architectures. We believe the next generation of intelligent software systems should not be designed rigidly, but **grown** — nurtured by Mother Programs that spawn, evaluate, and evolve the right capabilities for each moment.

- 🌐 Repository: [github.com/Infinite-Networker/The-Mother-Baby-Program-Paradigm](https://github.com/Infinite-Networker/The-Mother-Baby-Program-Paradigm)
- 📄 License: [MIT](LICENSE) — © 2024 Cherry Computer Ltd.
- 📬 Contact: Open a [GitHub Issue](https://github.com/Infinite-Networker/The-Mother-Baby-Program-Paradigm/issues) or [Discussion](https://github.com/Infinite-Networker/The-Mother-Baby-Program-Paradigm/discussions)

---

## 📚 Table of Contents

- [Philosophy](#-philosophy)
- [Key Concepts](#-key-concepts)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Implementation Examples](#-implementation-examples)
- [Baby Program Types](#-baby-program-types)
- [Use Cases](#-use-cases)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Research & Development](#-research--development)
- [License](#-license)

---

## 🧠 Philosophy

> *"Just as a mother nurtures her children, teaches them, and gives them autonomy over time,  
> a Mother Program spawns and governs Baby Programs."*

Traditional software architectures are built like rigid machines — fixed components, hardcoded pathways, brittle dependencies. When something breaks, the whole system stalls.

The Mother-Baby Paradigm proposes a fundamentally different model — one drawn from **life itself**:

| Traditional Thinking | Mother-Baby Thinking |
|----------------------|---------------------|
| Machines → fixed, deterministic | Organisms → adaptive, probabilistic |
| Failure = crash the system | Failure = signal for evolution |
| Scaling = add servers manually | Scaling = spawn new Baby Programs |
| Single monolith | Living ecosystem of specialized units |
| Code updates = redeployment | Learning = babies self-modify over time |

Read the full philosophy: [`docs/PHILOSOPHY.md`](docs/PHILOSOPHY.md)

---

## 🔑 Key Concepts

### 👶 Baby Programs
| Property | Description |
|----------|-------------|
| **Definition** | Light, modular programs operating semi-independently |
| **Behavior** | Reactive, adaptable, potentially self-modifying |
| **Examples** | AI agents, microservices, bots, specialized processors |
| **Lifecycle** | Born → Active ⇄ Processing ⇄ Resting → [Evolving] → Terminated |
| **Communication** | Via shared MessageBus (never direct calls) |

### 🧠 Mother Programs
| Property | Description |
|----------|-------------|
| **Definition** | Central intelligent core managing multiple Baby Programs |
| **Behavior** | Strategic, supervisory, decision-making focused |
| **Examples** | Orchestrators, AI supervisors, meta-programs |
| **Functions** | Spawn · Monitor · Evaluate · Terminate · Evolve |

### 📡 Message Bus
The nervous system of the paradigm. All Mother↔Baby and Baby↔Baby communication flows through a **publish/subscribe MessageBus**. This ensures:
- Complete decoupling between components
- Full message history for observability
- Easy testing via message replay

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   MOTHER PROGRAM LAYER                        │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Spawner  │ │ Evaluator │ │Supervisor│ │LifecycleManager│  │
│  └──────────┘ └───────────┘ └──────────┘ └───────────────┘  │
│               ┌──────────────────────────────┐               │
│               │      MotherProgram Core       │               │
│               │  spawn_baby · broadcast       │               │
│               │  terminate · get_status       │               │
│               └──────────────────────────────┘               │
└─────────────────────────┬────────────────────────────────────┘
                           │
               ┌───────────▼───────────┐
               │      MESSAGE BUS       │
               │ publish · subscribe    │
               │ direct · history       │
               └───────────┬───────────┘
                           │
     ┌─────────────────────┼──────────────────────┐
     │                     │                      │
┌────▼───────┐    ┌────────▼────────┐    ┌────────▼────────┐
│ WorkerBaby │    │     AIBaby      │    │   SensorBaby    │
│ Batch tasks│    │ Learns & Adapts │    │ Continuous Data │
└─────┬──────┘    └────────┬────────┘    └────────┬────────┘
      └──────────────────────┬───────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │   BabyProgram (Abstract)     │
              │  execute · report_metrics    │
              │  on_born · evolve · on_msg   │
              └─────────────────────────────┘
```

See the full SVG diagram: [`assets/designs/architecture_diagram.svg`](assets/designs/architecture_diagram.svg)  
See the ASCII diagram: [`docs/diagrams/architecture_ascii.py`](docs/diagrams/architecture_ascii.py)  
Read the full architecture doc: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## 📁 Project Structure

```
The-Mother-Baby-Program-Paradigm/
│
├── src/                            # Core framework source code
│   ├── __init__.py                 # Package entry point
│   ├── mother/
│   │   ├── mother_program.py       # MotherProgram — central orchestrator
│   │   ├── spawner.py              # Spawning policies (Fixed, Load-based)
│   │   ├── evaluator.py            # Performance scoring & recommendations
│   │   └── supervisor.py          # Health monitoring & auto-recovery
│   ├── baby/
│   │   ├── baby_program.py         # Abstract base class for all babies
│   │   ├── worker_baby.py          # General-purpose task worker
│   │   ├── ai_baby.py              # AI-powered learning baby
│   │   └── sensor_baby.py         # Continuous data stream reader
│   ├── communication/
│   │   └── message_bus.py          # Pub/Sub + Direct messaging bus
│   ├── lifecycle/
│   │   └── lifecycle_manager.py    # Background health & evolution threads
│   └── utils/
│       └── logger.py               # Consistent logging utility
│
├── examples/
│   ├── basic/
│   │   └── hello_mother_baby.py    # Minimal quickstart example
│   ├── advanced/
│   │   └── ai_temperature_pipeline.py  # Multi-baby AI pipeline
│   └── ai_agents/                  # (Coming soon)
│
├── tests/
│   ├── unit/
│   │   ├── test_mother_program.py  # MotherProgram unit tests
│   │   └── test_message_bus.py     # MessageBus unit tests
│   └── integration/
│       └── test_pipeline.py        # Full system integration tests
│
├── docs/
│   ├── PHILOSOPHY.md               # The paradigm's conceptual foundation
│   ├── ARCHITECTURE.md             # Technical architecture reference
│   └── diagrams/
│       └── architecture_ascii.py   # ASCII architecture diagram
│
├── assets/
│   └── designs/
│       └── architecture_diagram.svg # Visual SVG architecture diagram
│
├── CONTRIBUTING.md                 # Contributor guide
├── LICENSE                         # MIT License — © 2024 Cherry Computer Ltd.
├── requirements.txt                # Runtime dependencies
└── requirements-dev.txt            # Development dependencies
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Infinite-Networker/The-Mother-Baby-Program-Paradigm.git
cd The-Mother-Baby-Program-Paradigm

# (Optional) Create a virtual environment
python -m venv venv && source venv/bin/activate

# Install dependencies (pure Python — no external packages required for core)
pip install -r requirements.txt
```

### Hello, Mother-Baby World

```python
from src.mother.mother_program import MotherProgram, MotherConfig
from src.baby.worker_baby import WorkerBaby

# 1. Define your task handler
def square_numbers(data: dict) -> dict:
    n = data["number"]
    return {"input": n, "output": n ** 2}

# 2. Configure and start the Mother Program
mother = MotherProgram(MotherConfig(name="MyMother", max_babies=5))
mother.start()

# 3. Spawn a Baby Program
baby_id = mother.spawn_baby(WorkerBaby, task="square_numbers")
baby = mother._babies[baby_id]
baby._handler = square_numbers

# 4. Submit tasks
for n in [3, 7, 12]:
    baby.submit_task({"number": n})

import time; time.sleep(0.5)

# 5. Inspect results
print(baby.get_results())   # [{"input":3,"output":9}, ...]
print(baby.health_score)    # 1.0

# 6. Shutdown
mother.shutdown()
```

Run the full example:
```bash
python examples/basic/hello_mother_baby.py
```

---

## 💻 Implementation Examples

### Example 1: Worker Baby Pipeline

```python
# Batch-process data with multiple parallel Worker Babies

from src.mother.mother_program import MotherProgram, MotherConfig
from src.baby.worker_baby import WorkerBaby

mother = MotherProgram(MotherConfig(name="BatchMother", max_babies=10))
mother.start()

# Spawn 3 parallel workers
worker_ids = [mother.spawn_baby(WorkerBaby, task="transform") for _ in range(3)]

# Round-robin task distribution
for i, task_id in enumerate(range(100)):
    baby = mother._babies[worker_ids[task_id % 3]]
    baby.submit_task({"record_id": task_id, "value": task_id * 1.5})

import time; time.sleep(2.0)

# Gather results
for wid in worker_ids:
    w = mother._babies[wid]
    print(f"Worker {wid[:8]}: {w.task_count} tasks, health={w.health_score}")

mother.shutdown()
```

### Example 2: AI Learning Baby

```python
from src.baby.ai_baby import AIBaby

ai_id = mother.spawn_baby(AIBaby, task="classify_events")
ai = mother._babies[ai_id]

# Feed classified events
for category in ["error", "warning", "info", "error", "error"]:
    ai.submit_task({"type": category, "content": "log line here"})

import time; time.sleep(1.0)

# Check learning
patterns = ai.get_learned_patterns()
print(patterns["confidence"])
# {"error": 0.8, "warning": 0.3, "info": 0.2} — errors seen more, higher confidence
```

### Example 3: Sensor Monitoring with Alerts

```python
import random
from src.baby.sensor_baby import SensorBaby

def cpu_load_sensor() -> float:
    return random.uniform(10.0, 95.0)

sensor_id = mother.spawn_baby(
    SensorBaby,
    task="cpu_monitoring",
    config={"name": "CPUMonitor"},
)
sensor = mother._babies[sensor_id]
sensor._sensor_fn = cpu_load_sensor
sensor._alert_threshold = 80.0   # Alert when CPU > 80%
sensor._emit_interval = 1.0

# Subscribe to alerts
mother._message_bus.subscribe(
    "sensor_alert",
    lambda event, data, sender: print(f"🚨 CPU SPIKE: {data['reading']:.1f}%")
)
```

### Example 4: Custom Baby with Evolution

```python
class AdaptiveSorterBaby(BabyProgram):
    """Sorts lists, adapting its algorithm based on input size."""

    def on_born(self):
        self.algorithm_uses = {"quicksort": 0, "timsort": 0}

    def execute(self, task_data):
        data = task_data["items"]
        algo = "timsort" if len(data) < 100 else "quicksort"
        self.algorithm_uses[algo] += 1
        self.learned_data["preferred_algo"] = max(
            self.algorithm_uses, key=self.algorithm_uses.get
        )
        return sorted(data)

    def evolve(self):
        # After evolution, log which algorithm dominated
        self.logger.info(f"Algorithm preference: {self.learned_data.get('preferred_algo')}")

    def report_metrics(self):
        total = self.task_count + self.error_count
        return {
            "task_completion_rate": self.task_count / total if total else 0.0,
            "error_rate": self.error_count / total if total else 0.0,
            "response_time_ms": 5.0,
            "memory_usage_mb": 10.0,
            "cpu_percent": 2.0,
        }
```

---

## 👶 Baby Program Types

### Built-in Babies

| Class | File | Best For |
|-------|------|----------|
| `WorkerBaby` | `src/baby/worker_baby.py` | General CPU-bound tasks, batch processing |
| `AIBaby` | `src/baby/ai_baby.py` | Classification, inference, adaptive learning |
| `SensorBaby` | `src/baby/sensor_baby.py` | IoT sensors, real-time data streams, monitoring |

### Create Your Own

Any class that extends `BabyProgram` and implements `execute()` and `report_metrics()` is a valid Baby Program.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full guide.

---

## 🎯 Use Cases

| Domain | Use Case | Baby Type |
|--------|----------|-----------|
| **Data Engineering** | Parallel CSV/JSON transformation | `WorkerBaby` |
| **AI / ML** | Distributed model inference | `AIBaby` |
| **IoT** | Multi-sensor data aggregation | `SensorBaby` |
| **DevOps** | System health monitoring | `SensorBaby` |
| **Finance** | Real-time transaction processing | `WorkerBaby` |
| **NLP** | Text classification at scale | `AIBaby` |
| **Robotics** | Modular behavior controllers | Custom `BabyProgram` |
| **Game Dev** | NPC AI agents | Custom `BabyProgram` + `AIBaby` |
| **Security** | Threat detection pipelines | `SensorBaby` + `AIBaby` |
| **Healthcare** | Patient data stream analysis | `SensorBaby` + `AIBaby` |

---

## 📖 API Reference

### MotherProgram

```python
MotherProgram(config: MotherConfig)
    .start()                                       # Activate
    .spawn_baby(cls, task, config, tags) → str     # Spawn a baby
    .terminate_baby(id, graceful=True) → bool      # Kill a baby
    .restart_baby(id) → bool                       # Restart a baby
    .broadcast(event, data)                        # Message all babies
    .send_to_baby(id, event, data) → bool          # Direct message
    .get_status() → dict                           # Full snapshot
    .get_babies_by_tag(tag) → List[BabyProgram]    # Filter by tag
    .get_babies_by_state(state) → List[BabyProgram]# Filter by state
    .on_baby_born(callback)                        # Register hook
    .on_baby_died(callback)                        # Register hook
    .on_evolution(callback)                        # Register hook
    .shutdown(graceful=True)                       # Shut down all
```

### BabyProgram

```python
BabyProgram                       # Abstract base
    .start()                      # Begin processing
    .stop(graceful=True)          # Terminate
    .submit_task(data)            # Queue a task
    .on_event(event, callback)    # Register event handler
    .execute(task_data) → Any     # [ABSTRACT] Task logic
    .report_metrics() → dict      # [ABSTRACT] Metrics snapshot
    .on_born()                    # [HOOK] Setup
    .on_terminated()              # [HOOK] Cleanup
    .on_message(event, data)      # [HOOK] Handle bus messages
    .evolve()                     # [HOOK] Adapt from learning
```

### MessageBus

```python
MessageBus(history_size=100)
    .subscribe(event, callback)                    # Broadcast subscribe
    .subscribe_direct(recipient_id, callback)      # Direct subscribe
    .unsubscribe(event, callback)                  # Unsubscribe
    .publish(event, data, sender) → Message        # Broadcast publish
    .publish_direct(id, event, data, sender)       # Direct publish
    .get_history(event_filter=None) → List[Message]# Message history
    .get_stats() → dict                            # Bus statistics
    .shutdown()                                    # Shut down bus
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run only unit tests
python -m pytest tests/unit/ -v

# Run only integration tests
python -m pytest tests/integration/ -v
```

Expected output:
```
tests/unit/test_mother_program.py::TestMotherProgram::test_initial_state_is_active PASSED
tests/unit/test_mother_program.py::TestMotherProgram::test_spawn_baby_returns_id   PASSED
tests/unit/test_message_bus.py::TestMessageBus::test_publish_delivers_to_subscriber PASSED
tests/integration/test_pipeline.py::TestFullPipeline::test_full_worker_pipeline    PASSED
...
```

---

## 🤝 Contributing

We warmly welcome contributions! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for:
- Development setup instructions
- Coding standards and conventions
- How to create new Baby types
- Pull request process
- Testing requirements

---

## 🔬 Research & Development

The Mother-Baby Program Paradigm is a living research project. Areas of active exploration:

### Roadmap

- [ ] **Async Baby Programs** — asyncio-native execution model
- [ ] **Networked Mother Programs** — Multiple Mothers coordinating across machines
- [ ] **Visual Dashboard** — Real-time monitoring web UI
- [ ] **Genetic Algorithm Spawning** — Evolve baby configurations automatically
- [ ] **Baby DNA System** — Serialize and transfer baby learned states
- [ ] **Swarm Babies** — Babies that self-organize without Mother oversight
- [ ] **Plugin Architecture** — Hot-swappable baby modules
- [ ] **gRPC MessageBus** — Distributed, cross-language message passing

### Research Papers & Inspirations

- **Multi-Agent Systems** (Weiss, 1999) — Foundational concepts in agent coordination
- **Actor Model** (Hewitt et al., 1973) — Concurrency via message passing
- **Self-Organizing Systems** (Kauffman, 1993) — Emergence in complex adaptive systems
- **Cellular Automata** (Von Neumann, 1966) — Self-replicating system design
- **Swarm Intelligence** (Bonabeau et al., 1999) — Decentralized collective behavior

---

## 📜 License

```
MIT License

Copyright (c) 2024 Cherry Computer Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**Made with ❤️ by Cherry Computer Ltd.**

*Pioneering bio-inspired software architectures*

*© 2024 Cherry Computer Ltd. — All rights reserved under MIT License*

</div>
