"""
Basic Example: Hello Mother-Baby World
========================================
A minimal example demonstrating how to spin up a MotherProgram,
spawn a WorkerBaby, submit tasks, and inspect results.

Created by: Cherry Computer Ltd.
"""

import sys
import os
import time

# Allow running from the repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.mother.mother_program import MotherProgram, MotherConfig
from src.baby.worker_baby import WorkerBaby


# ── 1. Define a custom handler for the WorkerBaby ──────────────────────────

def square_numbers(data: dict) -> dict:
    """Simple handler: squares a number."""
    value = data.get("number", 0)
    result = value ** 2
    print(f"  ✦ WorkerBaby processed: {value}² = {result}")
    return {"input": value, "output": result}


# ── 2. Bootstrap the Mother Program ────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Mother-Baby Program Paradigm  ·  Cherry Computer Ltd.")
    print("=" * 60)

    # Configure and start the Mother Program
    config = MotherConfig(
        name="DemoMother",
        max_babies=5,
        health_check_interval=2.0,
        learning_enabled=False,   # Disable evolution for this demo
    )
    mother = MotherProgram(config)
    mother.start()
    print("\n[Mother] Started successfully.\n")

    # ── 3. Register lifecycle hooks ────────────────────────────────────────
    mother.on_baby_born(lambda b: print(f"[Hook] Baby born: {b.id[:8]} — class={b.__class__.__name__}"))
    mother.on_baby_died(lambda b: print(f"[Hook] Baby died: {b.id[:8]}"))

    # ── 4. Spawn a WorkerBaby ──────────────────────────────────────────────
    baby_id = mother.spawn_baby(
        WorkerBaby,
        task="square_numbers",
        config={"name": "SquareWorker"},
    )

    # Inject the custom handler (post-construction for this demo)
    baby = mother._babies[baby_id]
    baby._handler = square_numbers

    print(f"\n[Mother] Spawned baby: {baby_id[:8]}")
    print(f"[Mother] Status: {mother.get_status()['state']}\n")

    # ── 5. Submit tasks ────────────────────────────────────────────────────
    print("[Mother] Submitting tasks to baby...\n")
    for n in [3, 7, 12, 25, 100]:
        baby.submit_task({"number": n})

    time.sleep(1.5)  # Allow processing

    # ── 6. Inspect results ─────────────────────────────────────────────────
    results = baby.get_results()
    print(f"\n[Baby] Completed {baby.task_count} tasks.")
    print(f"[Baby] Results: {results}")
    print(f"[Baby] Health: {baby.health_score}")

    # ── 7. Broadcast a message to all babies ──────────────────────────────
    print("\n[Mother] Broadcasting 'clear_results'...")
    mother.broadcast("clear_results")
    time.sleep(0.2)

    # ── 8. Status snapshot ─────────────────────────────────────────────────
    print("\n[Mother] Full status snapshot:")
    status = mother.get_status()
    for bid, binfo in status["babies"].items():
        print(f"  Baby {bid[:8]}: state={binfo['state']}, health={binfo['health']}")

    # ── 9. Shutdown ────────────────────────────────────────────────────────
    print("\n[Mother] Shutting down...")
    mother.shutdown()
    print("[Mother] Shutdown complete.\n")
    print("=" * 60)


if __name__ == "__main__":
    main()
