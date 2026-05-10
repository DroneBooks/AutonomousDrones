# Volume 1 — Chapter 1: Hardware

> **Resources for the chapter "Drone Hardware: Components and Selection"**
> **Level:** Beginner

---

## Contents

```
VOLUME-1/01-Hardware/
├── README.md
└── thrust_calculator.py    # ✅ Specifications calculator
```

---

## Available Tools

### **thrust_calculator.py** — Specifications Calculator

Interactive tool with 4 calculators to size your drone before buying or assembling:

| Calculator | What it computes |
|------------|-----------------|
| **1. T:W (thrust/weight)** | Whether the drone will have enough power to fly |
| **2. Flight time** | Estimated endurance based on battery and power draw |
| **3. Motor KV** | Recommended KV range by drone category |
| **4. Blade tip speed** | Checks propeller safety limits |

```bash
python thrust_calculator.py
```

**Example (T:W):**
```
Number of motors: 4
Thrust per motor at full throttle (grams): 850
Total drone weight with battery (grams): 1500

  Total thrust (100% throttle)  :  3400 g
  Total weight                  :  1500 g
  Thrust-to-weight ratio (T:W)  :  2.27 : 1
  ✅  IDEAL — good maneuverability and flight time.
```

---

## Formulas Used

| Concept | Formula |
|---------|---------|
| T:W ratio | `(motors × motor_thrust) / total_weight` |
| Flight time | `(battery_Ah × efficiency%) / current_A × 60` |
| Estimated RPM | `KV × voltage × 0.85` (load factor) |
| Blade tip speed | `2π × radius_m × RPM / 60` |

---

## Book Reference

These calculators accompany **Volume 1, Chapter 1: Hardware** of the book
*Autonomous Drones I: Hardware, Ardupilot and MAVLink*.

Related topics in the chapter:
- Motor and propeller selection
- LiPo battery sizing
- Thrust-to-weight ratio for different applications
- Mechanical safety in rotating components

---

## Requirements

- Python 3.10+
- No external dependencies (standard library only)

---

**Last updated:** April 2026 | DroneBooks
