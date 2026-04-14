import os
import subprocess
import sys


# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────

def ask(prompt, default):
    raw = input(f"  {prompt} [{default}]: ").strip()
    return raw if raw else str(default)


def ask_float(prompt, default):
    while True:
        raw = input(f"  {prompt} [{default}]: ").strip()
        val = raw if raw else str(default)
        try:
            return float(val)
        except ValueError:
            print("    Please enter a number.")


def ask_int(prompt, default):
    while True:
        raw = input(f"  {prompt} [{default}]: ").strip()
        val = raw if raw else str(default)
        try:
            return int(val)
        except ValueError:
            print("    Please enter an integer.")


def ask_array(prompt, default_list):
    """Ask for a comma-separated list of floats. Returns list of floats."""
    default_str = ", ".join(str(v) for v in default_list)
    while True:
        raw = input(f"  {prompt} [{default_str}]: ").strip()
        if not raw:
            return default_list
        try:
            return [float(x.strip()) for x in raw.split(",")]
        except ValueError:
            print("    Please enter comma-separated numbers.")


def ask_choice(prompt, options):
    """Show numbered options, return chosen string value."""
    print(f"\n  {prompt}")
    for i, opt in enumerate(options, 1):
        print(f"    {i}) {opt}")
    while True:
        raw = input(f"  Choice [1]: ").strip()
        val = raw if raw else "1"
        try:
            idx = int(val) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print(f"    Please enter a number between 1 and {len(options)}.")


# ─────────────────────────────────────────
# FORMATTING HELPERS
# ─────────────────────────────────────────

def fmt(v):
    if isinstance(v, int):
        return str(v)
    s = f"{v:.6g}"
    # Normalise exponent: Python emits e-06, DSL convention is e-6
    s = s.replace("e-0", "e-").replace("e+0", "e+")
    return s


def fmt_array(arr):
    return "[" + ", ".join(fmt(x) for x in arr) + "]"


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 60)
    print("  eCherry Reactor Builder")
    print("  Generates a .reactor DSL file and eCherry Modelica output")
    print("=" * 60)

    # ── Step 2: DSL filename ──────────────────────────────────────
    while True:
        filename = input("\n  DSL filename (no extension, e.g. my_reactor): ").strip()
        if filename and all(c.isalnum() or c == "_" for c in filename):
            break
        print("    Only alphanumeric characters and underscores allowed, cannot be empty.")

    # ── Step 3: Reactor name ──────────────────────────────────────
    while True:
        reactor_name = input(
            "  Reactor name (used inside the .reactor file, e.g. My_Reactor): "
        ).strip()
        if reactor_name and all(c.isalnum() or c == "_" for c in reactor_name):
            break
        print("    Only alphanumeric characters and underscores allowed, cannot be empty.")

    # ── Step 4: Setup ─────────────────────────────────────────────
    setup = ask_choice(
        "Select reactor setup:",
        [
            "continuous_0D_alkaline",
            "batch_0D_alkaline",
            "continuous_0D_ammonia",
            "continuous_1D_alkaline",
        ],
    )

    is_ammonia = setup == "continuous_0D_ammonia"
    is_1d      = setup == "continuous_1D_alkaline"

    # ── Step 5: Parameters ────────────────────────────────────────

    # Electrolyte mode (AWE 0D only)
    if setup in ("continuous_0D_alkaline", "batch_0D_alkaline"):
        mode = ask_choice("Electrolyte mode:", ["simple", "KOH"])
    else:
        mode = "simple"

    # --- Electrical ---
    print("\n--- Electrical ---")
    voltage_defaults = {
        "continuous_0D_alkaline": -2.5,
        "batch_0D_alkaline":      -2.5,
        "continuous_0D_ammonia":  -2.0,
        "continuous_1D_alkaline": -2.3,
    }
    voltage = ask_float("Voltage (must be negative)", voltage_defaults[setup])

    # --- Geometry ---
    print("\n--- Geometry ---")
    if is_ammonia:
        X_default          = 0.001
        X_membrane_default = 115e-6
        Y_default          = 0.5
        Z_default          = 1.0
        cond0_default      = 1.0
        dX_default         = 0.01
    elif is_1d:
        X_default          = 0.01
        X_membrane_default = 5e-6
        Y_default          = 1.0
        Z_default          = 1.0
        cond0_default      = 1.0
        dX_default         = 1e-6
    elif mode == "KOH":
        X_default          = 0.01
        X_membrane_default = 0.0005
        Y_default          = 0.05
        Z_default          = 0.05
        cond0_default      = 1.0
        dX_default         = 1e-6
    else:
        X_default          = 0.01
        X_membrane_default = 0.0005
        Y_default          = 1.0
        Z_default          = 1.0
        cond0_default      = 1.0
        dX_default         = 1e-6

    geo_X          = ask_float("X (electrode gap width)",      X_default)
    geo_X_membrane = ask_float("X_membrane (membrane thickness)", X_membrane_default)
    geo_Y          = ask_float("Y (height)",                   Y_default)
    geo_Z          = ask_float("Z (depth)",                    Z_default)
    geo_cond0      = ask_float("cond0 (initial conductivity)", cond0_default)
    geo_dX         = ask_float("dX (spatial step)",            dX_default)
    if is_ammonia:
        geo_X_electrode = ask_float("X_electrode (electrode thickness)", 0.005)

    # --- Conditions ---
    print("\n--- Conditions ---")
    if is_ammonia:
        T0_default           = 333.15
        Tenvironment_default = 288.15
        p_default            = 100000.0
    else:
        T0_default           = 300.0
        Tenvironment_default = 293.15
        p_default            = 1.0

    T0           = ask_float("T0 (initial temperature, K)", T0_default)
    Tenvironment = ask_float("Tenvironment (K)",            Tenvironment_default)
    p            = ask_float("p (pressure)",                p_default)

    # --- Species & Concentrations ---
    print("\n--- Species & Concentrations ---")
    if is_ammonia:
        species = ["O2", "H2", "N2", "NH3", "OHm", "Kp", "H2O"]
        print(f"  Species (fixed): {species}")
        c0_electrolyte = ask_array(
            "Electrolyte concentrations", [0, 1.45e-12, 0, 0, 6000, 6000, 55e3]
        )
        c0_gas_channel = ask_array(
            "Gas channel concentrations", [0, 0, 1, 0, 0, 0, 0]
        )
    elif mode == "KOH":
        species = ["O2", "H2", "Hp", "OHm", "Kp", "H2O"]
        print(f"  Species (fixed): {species}")
        c0 = ask_array("Concentrations", [0, 1.45e-12, 1e-4, 6000, 6000, 55e3])
    else:
        species = ["O2", "H2", "Hp", "OHm", "H2O"]
        print(f"  Species (fixed): {species}")
        c0 = ask_array("Concentrations", [0, 1.45e-12, 1e-4, 6000, 55e3])

    # --- Reactions ---
    print("\n--- Reactions ---")
    if is_ammonia:
        print("  Anode:   OERdummy")
        print("  Cathode: [HERdummy, NRRdummy]  (gas diffusion — fixed)")
    else:
        print("  Anode:   OERdummy")
        print("  Cathode: HERdummy  (fixed)")

    # --- Electrolyte (not ammonia) ---
    if not is_ammonia:
        print("\n--- Electrolyte ---")
        kappa_anode   = ask_float("kappa_anode",   75.0)
        kappa_cathode = ask_float("kappa_cathode", 85.0)

    # --- Diaphragm ---
    print("\n--- Diaphragm ---")
    diaphragm_kappa = ask_float("kappa", 38.0)

    # --- Diffusion Layer (1D only) ---
    if is_1d:
        print("\n--- Diffusion Layer ---")
        X_difflayer        = ask_float("X_difflayer",                   1e-6)
        kappa_anode_diff   = ask_float("kappa_anode (diffusion layer)", 85.0)
        kappa_cathode_diff = ask_float("kappa_cathode (diffusion layer)", 74.0)
        n_slices           = ask_int(  "n_slices",                      10)

    # --- Gas Channel (ammonia only) ---
    if is_ammonia:
        print("\n--- Gas Channel ---")
        mol_vec_frac0 = ask_array("mol_vec_frac0", [0, 0, 1, 0, 0, 0, 0])
        gc_slices     = ask_int(  "slices",         10)
        gc_t          = ask_float("t (residence time, s)", 5.0)

    # --- Simulation ---
    print("\n--- Simulation ---")
    stop_time_defaults = {
        "continuous_0D_ammonia":  30.0,
        "continuous_1D_alkaline":  5.0,
    }
    stop_time = ask_float("stop_time", stop_time_defaults.get(setup, 50.0))

    # ──────────────────────────────────────────────────────────────
    # Build DSL content
    # ──────────────────────────────────────────────────────────────

    lines = []
    lines.append(f"reactor {reactor_name} {{")

    if is_ammonia:
        lines.append(f"  setup:   {setup}")
        lines.append(f"  voltage: {fmt(voltage)}")
    elif is_1d:
        lines.append(f"  setup:            {setup}")
        lines.append(f"  electrolyte_mode: {mode}")
        lines.append(f"  voltage:          {fmt(voltage)}")
    else:
        lines.append(f"  setup: {setup}")
        lines.append(f"  electrolyte_mode: {mode}")
        lines.append(f"  voltage: {fmt(voltage)}")

    lines.append("")
    lines.append(f"  species: [{', '.join(species)}]")
    lines.append("")

    # Reactions
    lines.append("  reactions {")
    if is_ammonia:
        lines.append("    anode:        OERdummy")
        lines.append("    cathode:      [HERdummy, NRRdummy]")
        lines.append("    cathode_type: gas_diffusion")
    else:
        lines.append("    anode:   OERdummy")
        lines.append("    cathode: HERdummy")
    lines.append("  }")

    lines.append("")

    # Geometry
    lines.append("  geometry {")
    if is_ammonia:
        lines.append(f"    X:           {fmt(geo_X)}")
        lines.append(f"    X_membrane:  {fmt(geo_X_membrane)}")
        lines.append(f"    X_electrode: {fmt(geo_X_electrode)}")
        lines.append(f"    Y:           {fmt(geo_Y)}")
        lines.append(f"    Z:           {fmt(geo_Z)}")
        lines.append(f"    cond0:       {fmt(geo_cond0)}")
        lines.append(f"    dX:          {fmt(geo_dX)}")
    else:
        lines.append(f"    X:          {fmt(geo_X)}")
        lines.append(f"    X_membrane: {fmt(geo_X_membrane)}")
        lines.append(f"    Y:          {fmt(geo_Y)}")
        lines.append(f"    Z:          {fmt(geo_Z)}")
        lines.append(f"    cond0:      {fmt(geo_cond0)}")
        lines.append(f"    dX:         {fmt(geo_dX)}")
    lines.append("  }")

    lines.append("")

    # Conditions
    inflow_scale = 0.05 if is_1d else 0.005
    lines.append("  conditions {")
    lines.append(f"    T0:           {fmt(T0)}")
    lines.append(f"    Tenvironment: {fmt(Tenvironment)}")
    lines.append(f"    p:            {fmt(p)}")
    if is_1d:
        lines.append(f"    inflow_scale: {fmt(inflow_scale)}")
    lines.append("  }")

    lines.append("")

    # Concentrations
    if is_ammonia:
        lines.append("  concentrations {")
        lines.append(f"    electrolyte: {fmt_array(c0_electrolyte)}")
        lines.append(f"    gas_channel: {fmt_array(c0_gas_channel)}")
        lines.append("  }")
    else:
        lines.append(f"  concentrations: {fmt_array(c0)}")

    lines.append("")

    # Electrolyte block (not ammonia)
    if not is_ammonia:
        lines.append("  electrolyte {")
        lines.append(f"    kappa_anode:   {fmt(kappa_anode)}")
        lines.append(f"    kappa_cathode: {fmt(kappa_cathode)}")
        lines.append("  }")
        lines.append("")

    # Diaphragm
    lines.append("  diaphragm {")
    lines.append(f"    kappa: {fmt(diaphragm_kappa)}")
    lines.append("  }")

    # Diffusion layer (1D only)
    if is_1d:
        lines.append("")
        lines.append("  diffusion_layer {")
        lines.append(f"    X_difflayer:   {fmt(X_difflayer)}")
        lines.append(f"    kappa_anode:   {fmt(kappa_anode_diff)}")
        lines.append(f"    kappa_cathode: {fmt(kappa_cathode_diff)}")
        lines.append(f"    n_slices:      {n_slices}")
        lines.append("  }")

    # Gas channel (ammonia only)
    if is_ammonia:
        lines.append("")
        lines.append("  gas_channel {")
        lines.append(f"    mol_vec_frac0: {fmt_array(mol_vec_frac0)}")
        lines.append(f"    slices: {gc_slices}")
        lines.append(f"    t: {fmt(gc_t)}")
        lines.append("  }")

    lines.append("")
    lines.append("  simulation {")
    lines.append(f"    stop_time: {fmt(stop_time)}")
    lines.append("  }")

    lines.append("}")

    dsl_content = "\n".join(lines) + "\n"

    # ──────────────────────────────────────────────────────────────
    # Write the file
    # ──────────────────────────────────────────────────────────────

    os.makedirs("dsl", exist_ok=True)
    output_path = f"dsl/{filename}.reactor"
    with open(output_path, "w") as f:
        f.write(dsl_content)

    print(f"\n✓ DSL file written to dsl/{filename}.reactor")
    print("\nRunning generator...")

    result = subprocess.run(
        [sys.executable, "run.py", f"dsl/{filename}.reactor"],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.returncode != 0:
        print("Generator error:")
        print(result.stderr)
    else:
        print(f"✓ Generation complete.")
        print(f"  Model.mo     → results/generated/{filename}/Model.mo")
        print(f"  UserInput.mo → results/generated/{filename}/UserInput.mo")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
