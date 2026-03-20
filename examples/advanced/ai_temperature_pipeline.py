"""
Advanced Example: Multi-Baby AI Pipeline
==========================================
Demonstrates a realistic pipeline where:
  - A MotherProgram manages multiple AIBabies and a SensorBaby
  - The SensorBaby reads simulated temperature data
  - AIBabies classify temperature anomalies
  - The Mother evolves the system after a monitoring period

Created by: Cherry Computer Ltd.
"""

import sys
import os
import time
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.mother.mother_program import MotherProgram, MotherConfig
from src.baby.ai_baby import AIBaby
from src.baby.sensor_baby import SensorBaby


# ── Temperature sensor simulation ──────────────────────────────────────────

def temperature_sensor() -> float:
    """Simulates a factory floor temperature sensor (°C)."""
    base_temp = 22.0
    spike = random.choices([0, random.uniform(15, 25)], weights=[0.85, 0.15])[0]
    noise = random.uniform(-1.0, 1.0)
    return round(base_temp + spike + noise, 2)


# ── Event handlers ─────────────────────────────────────────────────────────

def on_sensor_alert(event: str, data: dict, sender: str) -> None:
    print(f"  🚨 ALERT from {sender[:8]}: temp={data['reading']}°C "
          f"(threshold={data['threshold']}°C)")


def on_sensor_reading(event: str, data: dict, sender: str) -> None:
    # Feed readings into AI babies for classification
    pass  # Handled via direct task submission below


# ── Main pipeline ───────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  AI Temperature Pipeline  ·  Cherry Computer Ltd.")
    print("=" * 65)

    # Mother configuration
    config = MotherConfig(
        name="FactoryMother",
        max_babies=10,
        health_check_interval=3.0,
        evolution_interval=15.0,
        learning_enabled=True,
    )
    mother = MotherProgram(config)

    # Wire evolution hook
    def on_evolve(snapshot):
        print(f"\n[Evolution] Babies: {snapshot['total_babies']} | "
              f"State: {snapshot['state']}")
        for bid, binfo in snapshot["babies"].items():
            print(f"  ↳ {binfo['class']} {bid[:8]}: health={binfo['health']}, "
                  f"state={binfo['state']}")
        print()

    mother.on_evolution(on_evolve)
    mother.start()

    # Subscribe to sensor events on the message bus
    mother._message_bus.subscribe("sensor_alert", on_sensor_alert)

    # ── Spawn Sensor Baby ──────────────────────────────────────────────────
    print("\n[Mother] Spawning SensorBaby...")
    sensor_id = mother.spawn_baby(
        SensorBaby,
        task="factory_temperature",
        config={"name": "TempSensor"},
    )
    # Re-configure after spawn (demo approach)
    sensor_baby = mother._babies[sensor_id]
    sensor_baby._sensor_fn = temperature_sensor
    sensor_baby._alert_threshold = 35.0
    sensor_baby._emit_interval = 0.8

    # ── Spawn AI Classifier Babies ─────────────────────────────────────────
    print("[Mother] Spawning 3 AIBabies for classification...")
    ai_ids = []
    for i in range(3):
        ai_id = mother.spawn_baby(
            AIBaby,
            task=f"classify_temperature_{i+1}",
            config={"name": f"Classifier-{i+1}"},
        )
        ai_ids.append(ai_id)

    print(f"\n[Mother] All babies running. Monitoring for 10 seconds...\n")

    # ── Feed sensor readings into AI babies ────────────────────────────────
    start_time = time.time()
    ai_index = 0
    while time.time() - start_time < 10:
        reading = temperature_sensor()
        task_data = {
            "type": "temperature",
            "content": reading,
            "unit": "celsius",
            "source": "factory_floor",
        }
        # Round-robin across AI babies
        ai_baby = mother._babies.get(ai_ids[ai_index % len(ai_ids)])
        if ai_baby:
            ai_baby.submit_task(task_data)
        ai_index += 1
        time.sleep(0.5)

    # ── Print AI learning stats ─────────────────────────────────────────────
    print("\n" + "─" * 65)
    print("[Results] AI Baby Learning Patterns:")
    for ai_id in ai_ids:
        baby = mother._babies.get(ai_id)
        if baby:
            patterns = baby.get_learned_patterns()
            metrics = baby.report_metrics()
            print(f"\n  AIBaby {ai_id[:8]}:")
            print(f"    Tasks processed : {baby.task_count}")
            print(f"    Confidence      : {patterns['confidence']}")
            print(f"    Learning rate   : {patterns['learning_rate']}")
            print(f"    Avg accuracy    : {metrics.get('accuracy', 0):.2%}")

    # ── Sensor summary ─────────────────────────────────────────────────────
    print(f"\n[Results] SensorBaby readings summary:")
    print(f"    Readings collected : {sensor_baby.task_count}")
    print(f"    Average temp       : {sensor_baby.get_average()}°C")
    print(f"    Alert count        : {sensor_baby.report_metrics()['alert_count']}")

    # ── Shutdown ────────────────────────────────────────────────────────────
    print("\n[Mother] Initiating graceful shutdown...")
    mother.shutdown(graceful=True)
    print("[Mother] Pipeline complete.\n")
    print("=" * 65)


if __name__ == "__main__":
    main()
