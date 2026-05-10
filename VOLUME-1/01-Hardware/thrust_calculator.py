#!/usr/bin/env python3
"""
Volume 1 — Chapter 1: Hardware
Specifications calculator for multirotor drones.
Helps size components before buying or assembling.
"""

def separator(title=""):
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print('=' * 60)
    else:
        print('-' * 60)


# ─── 1. Thrust-to-Weight Ratio ───────────────────────────────────

def calculate_thrust_to_weight():
    separator("CALCULATOR: Thrust-to-Weight Ratio (T:W)")
    print("Determines whether the drone has enough power to fly.")
    print("Recommended value: 2:1 — 3:1 for FPV / autonomous drones\n")

    try:
        num_motors   = int(input("Number of motors (e.g. 4 for quadrotor): "))
        motor_thrust = float(input("Thrust per motor at full throttle (grams): "))
        total_weight = float(input("Total drone weight with battery (grams): "))
    except ValueError:
        print("[ERROR] Please enter valid numeric values.")
        return

    total_thrust = num_motors * motor_thrust
    ratio        = total_thrust / total_weight

    separator()
    print(f"  Total thrust (100% throttle) : {total_thrust:.0f} g")
    print(f"  Total weight                 : {total_weight:.0f} g")
    print(f"  Thrust-to-weight ratio (T:W) : {ratio:.2f} : 1")
    separator()

    if ratio < 1.5:
        print("  ⛔  INSUFFICIENT — the drone will not take off properly.")
    elif ratio < 2.0:
        print("  ⚠️   TIGHT — suitable for stationary photography.")
    elif ratio <= 3.5:
        print("  ✅  IDEAL — good maneuverability and flight time.")
    else:
        print("  🚀  OVERPOWERED — suitable for racing / aerobatics.")


# ─── 2. Estimated Flight Time ────────────────────────────────────

def calculate_flight_time():
    separator("CALCULATOR: Estimated Flight Time")
    print("Estimates flight endurance based on battery and power draw.\n")

    try:
        capacity_mah = float(input("Battery capacity (mAh, e.g. 5000): "))
        current_a    = float(input("Average flight current draw (A, e.g. 20): "))
        efficiency   = float(input("Estimated efficiency (%, default 80): ") or "80")
    except ValueError:
        print("[ERROR] Please enter valid numeric values.")
        return

    # Usable capacity applying efficiency (don't fully discharge the battery)
    usable_capacity_ah = (capacity_mah / 1000.0) * (efficiency / 100.0)
    flight_time_min    = (usable_capacity_ah / current_a) * 60.0

    separator()
    print(f"  Battery capacity             : {capacity_mah:.0f} mAh")
    print(f"  Average current draw         : {current_a:.1f} A")
    print(f"  Applied efficiency           : {efficiency:.0f}%")
    print(f"  Estimated flight time        : {flight_time_min:.1f} min")
    separator()

    if flight_time_min < 5:
        print("  ⛔  Very short — check power draw or increase battery.")
    elif flight_time_min < 10:
        print("  ⚠️   Low endurance — enough for short practice sessions.")
    elif flight_time_min <= 25:
        print("  ✅  Good endurance — suitable for standard missions.")
    else:
        print("  ✅  Excellent endurance — efficient platform.")

    print(f"\n  Tip: For {flight_time_min * 2:.0f} min of flight, you would need")
    print(f"  {capacity_mah * 2:.0f} mAh or halve the weight/power draw.")


# ─── 3. Motor Selection (KV) ─────────────────────────────────────

def recommend_motor_kv():
    separator("CALCULATOR: Motor KV and Propeller Selection")
    print("Relates motor KV, battery voltage and propeller size.")
    print("Rule: KV × Voltage ≈ no-load RPM\n")

    KV_TABLE = [
        # (type, drone_weight_g, prop_inch, lipo_cells, kv_min, kv_max)
        ("Micro / Racing 3\"",    250,   3,  4, 2400, 3000),
        ("Mini / FPV 5\"",        600,   5,  4, 1700, 2400),
        ("Freestyle 5-6\"",       800,   6,  4, 1500, 2000),
        ("Photography 7-8\"",    1500,   8,  4,  800, 1200),
        ("Photography 10\"",     2500,  10,  6,  400,  700),
        ("Heavy-lift 12-15\"",   5000,  13,  6,  200,  400),
    ]

    print("  Available categories:")
    for i, (drone_type, _, _, _, _, _) in enumerate(KV_TABLE, 1):
        print(f"  [{i}] {drone_type}")

    try:
        sel = int(input("\n  Select category: ")) - 1
        if not 0 <= sel < len(KV_TABLE):
            raise ValueError
    except ValueError:
        print("[ERROR] Invalid selection.")
        return

    drone_type, weight, prop, cells, kv_min, kv_max = KV_TABLE[sel]
    voltage = cells * 3.7  # Nominal LiPo voltage

    separator()
    print(f"  Category                     : {drone_type}")
    print(f"  Estimated drone weight       : {weight} g")
    print(f"  Recommended propeller        : {prop}\"")
    print(f"  Recommended battery          : {cells}S LiPo ({voltage:.1f}V nominal)")
    print(f"  Recommended KV range         : {kv_min} — {kv_max} KV")
    print(f"  Estimated RPM (at full load) : {int(kv_max * voltage * 0.85)} rpm")
    separator()
    print("  Note: Indicative values. Refer to manufacturer datasheets")
    print("  for exact thrust figures per propeller.")


# ─── 4. Blade Tip Speed (Safety) ─────────────────────────────────

def calculate_blade_tip_speed():
    separator("CALCULATOR: Blade Tip Speed")
    print("Checks whether the propeller is within safe operating limits.")
    print("Recommended limit: < 120 m/s (Mach 0.35)\n")

    try:
        kv       = float(input("Motor KV: "))
        voltage  = float(input("Battery voltage (V, e.g. 14.8 for 4S): "))
        diameter = float(input("Propeller diameter (inches, e.g. 5): "))
    except ValueError:
        print("[ERROR] Please enter valid numeric values.")
        return

    rpm_no_load  = kv * voltage
    rpm_loaded   = rpm_no_load * 0.85           # ~85% under load
    radius_m     = (diameter * 0.0254) / 2.0    # inches → metres
    tip_speed_ms = (2 * 3.14159 * radius_m * rpm_loaded) / 60.0

    separator()
    print(f"  No-load RPM (KV × V)         : {rpm_no_load:.0f}")
    print(f"  Estimated loaded RPM         : {rpm_loaded:.0f}")
    print(f"  Propeller radius             : {radius_m * 100:.1f} cm")
    print(f"  Blade tip speed              : {tip_speed_ms:.1f} m/s")
    separator()

    if tip_speed_ms < 100:
        print("  ✅  Safe — within normal operating limits.")
    elif tip_speed_ms < 120:
        print("  ⚠️   At the limit — use carbon fibre propeller.")
    else:
        print("  ⛔  DANGEROUS — risk of propeller failure.")
        print("  → Reduce KV, voltage or propeller size.")


# ─── Main Menu ───────────────────────────────────────────────────

def main():
    separator("DroneAcademy — Hardware Calculator")
    print("  Volume 1, Chapter 1: Hardware")
    print("  Sizing tool for your drone components\n")

    options = {
        '1': ("Thrust-to-weight ratio (T:W)",   calculate_thrust_to_weight),
        '2': ("Estimated flight time",           calculate_flight_time),
        '3': ("Motor selection (KV)",            recommend_motor_kv),
        '4': ("Blade tip speed",                 calculate_blade_tip_speed),
        '5': ("Exit", None),
    }

    while True:
        separator("MAIN MENU")
        for key, (desc, _) in options.items():
            print(f"  [{key}] {desc}")

        choice = input("\n  Select option: ").strip()

        if choice not in options:
            print("\n[ERROR] Invalid option.")
            continue

        desc, func = options[choice]
        if func is None:
            print("\n[OK] Goodbye!\n")
            break

        func()
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
