# ============================================================
# DUAL-BAND KOCH FRACTAL DIPOLE
# UHF 430 MHz  +  L-band 1.4 GHz
# Kapton substrate - Helmet-conformal starting design
# HFSS / PyAEDT 1.6.0 / AEDT 2025 R2 Student
# ============================================================

import os
import math
from ansys.aedt.core import Hfss, settings

# --- Workarounds for AEDT Student 2025 R2 ---
os.environ["PYAEDT_USE_PRE_GRPC_ARGS"] = "True"
settings.grpc_secure_mode = False

# ============================================================
# USER PARAMETERS
# ============================================================

PROJECT_PATH = r"C:\Users\User\Desktop\SIH\DualBand_Koch_CPS.aedt"
AEDT_VERSION = "2025.2"

# Target bands
F_UHF = 0.43            # GHz
F_L   = 1.40            # GHz

# Kapton substrate
EPS_R = 3.4             # relative permittivity
TAND  = 0.002           # loss tangent
H_SUB = 0.30            # mm  (100 µm Kapton)
TCU   = 0.035           # mm  (1 oz copper)

# Koch dipole geometry
ARM_LEN     = 111.0      # mm - physical length of each arm
FEED_GAP    = 2.0       # mm
TRACE_WIDTH = 1.5       # mm
KOCH_ITER   = 2         # fractal iteration

# Substrate``
WSUB = 2.0 * (0.30 * ARM_LEN + TRACE_WIDTH + 5.0)# enough for Koch bumps
LSUB = 2.0 * ARM_LEN + FEED_GAP + 10.0      # margin on both ends

# Airbox
AIR_CLEARANCE = 150.0   # must be ≥ λ/4 at UHF

# Frequency sweep
SWEEP_START = 0.3       # GHz
SWEEP_STOP  = 1.6       # GHz
NUM_POINTS  = 131


# ============================================================
# KOCH GEOMETRY GENERATOR
# ============================================================

def koch_segment(p1, p2, iteration):
    """Recursively generate Koch curve points in the XY plane."""
    if iteration == 0:
        return [p1, p2]

    x1, y1 = p1
    x2, y2 = p2

    dx = (x2 - x1) / 3.0
    dy = (y2 - y1) / 3.0

    pA = (x1 + dx, y1 + dy)
    pB = (x1 + 2.0 * dx, y1 + 2.0 * dy)

    vx = pB[0] - pA[0]
    vy = pB[1] - pA[1]

    angle = math.radians(60.0)
    px = pA[0] + vx * math.cos(angle) - vy * math.sin(angle)
    py = pA[1] + vx * math.sin(angle) + vy * math.cos(angle)
    pPeak = (px, py)

    first  = koch_segment(p1,  pA,    iteration - 1)
    second = koch_segment(pA,  pPeak, iteration - 1)
    third  = koch_segment(pPeak, pB,  iteration - 1)
    fourth = koch_segment(pB,  p2,    iteration - 1)

    return first[:-1] + second[:-1] + third[:-1] + fourth


# ============================================================
# MATERIALS
# ============================================================

def create_kapton(hfss):
    materials = hfss.materials
    if "Kapton_Custom" not in materials.material_keys:
        mat = materials.add_material("Kapton_Custom")
        mat.permittivity = EPS_R
        mat.dielectric_loss_tangent = TAND
        print("   Created Kapton_Custom material")
    else:
        print("   Kapton material already exists")


# ============================================================
# GEOMETRY
# ============================================================

def create_substrate(hfss):
    return hfss.modeler.create_box(
        origin=[-WSUB/2, -LSUB/2, 0],
        sizes=[WSUB, LSUB, H_SUB],
        name="Substrate",
        material="Kapton_Custom"
    )


def create_arm(hfss, arm_name, y_start, y_end):
    """Create one Koch arm on top of the substrate."""
    p1 = (0.0, y_start)
    p2 = (0.0, y_end)

    points = koch_segment(p1, p2, KOCH_ITER)

    # Shift up by TCU/2 so the ribbon sits flush on the substrate
    z_arm = H_SUB + TCU / 2.0

    poly_points = [[x, y, z_arm] for (x, y) in points]

    arm = hfss.modeler.create_polyline(
        points=poly_points,
        name=arm_name,
        material="copper",
        xsection_type="Rectangle",
        xsection_width=TRACE_WIDTH,
        xsection_height=TCU,
    )
    return arm


def create_airbox(hfss):
    return hfss.modeler.create_box(
        origin=[
            -WSUB/2 - AIR_CLEARANCE,
            -LSUB/2 - AIR_CLEARANCE,
            -AIR_CLEARANCE
        ],
        sizes=[
            WSUB + 2 * AIR_CLEARANCE,
            LSUB + 2 * AIR_CLEARANCE,
            H_SUB + 2 * AIR_CLEARANCE
        ],
        name="AirBox",
        material="air"
    )


def create_lumped_port(hfss):
    """Lumped port bridging the feed gap between the two Koch arms."""
    port_width = TRACE_WIDTH * 3.0
    z_port = H_SUB + TCU / 2.0

    port_sheet = hfss.modeler.create_rectangle(
        orientation="XY",
        origin=[-port_width / 2.0, -FEED_GAP / 2.0, z_port],
        sizes=[port_width, FEED_GAP],
        name="Lumped_Port"
    )

    hfss.lumped_port(
        assignment=port_sheet.name,
        integration_line=[
            [0, -FEED_GAP / 2.0, z_port],
            [0,  FEED_GAP / 2.0, z_port]
        ],
        impedance=50,
        name="Port1"
    )
    print("   50-ohm lumped port created")


# ============================================================
# SETUPS
# ============================================================

def create_solution_setup(hfss):
    setup = hfss.create_setup(name="Setup_UHF")
    setup.props["Frequency"]     = "{}GHz".format(F_UHF)
    setup.props["MaximumPasses"] = 6
    setup.props["MaximumDeltaS"] = 0.0
    setup.props["MinimumPasses"] = 2
    setup.update()
    print("   Adaptive solution setup created ({} GHz)".format(F_UHF))


def create_frequency_sweep(hfss):
    hfss.create_linear_count_sweep(
        setup="Setup_UHF",
        unit="GHz",
        start_frequency=SWEEP_START,
        stop_frequency=SWEEP_STOP,
        num_of_freq_points=NUM_POINTS,
        name="Sweep_UHF_L",
        save_fields=False
    )
    print("   Frequency sweep {}-{} GHz created".format(SWEEP_START, SWEEP_STOP))


# ============================================================
# MAIN
# ============================================================

def main():
    import traceback

    print("=" * 60)
    print("DUAL-BAND KOCH FRACTAL DIPOLE")
    print("UHF 430 MHz  +  L-band 1.4 GHz")
    print("=" * 60)
    print("Substrate : Kapton (er={}, h={} mm)".format(EPS_R, H_SUB))
    print("Arm length: {} mm per arm".format(ARM_LEN))
    print("Koch iter : {}".format(KOCH_ITER))
    print("Trace width: {} mm".format(TRACE_WIDTH))
    print("Substrate : {} x {} mm".format(WSUB, LSUB))
    print()

    hfss = None
    try:
        print("STEP 1: launching AEDT...")
        hfss = Hfss(
            version=AEDT_VERSION,
            non_graphical=False,
            new_desktop=True,        # spawn fresh session
            student_version=True,
            close_on_exit=False,
            remove_lock=True,
        )
        print("STEP 1 OK: AEDT running, design =", hfss.design_name)

        hfss.solution_type = "DrivenModal"
        hfss.modeler.model_units = "mm"

        print("STEP 2: saving project...")
        hfss.save_project(PROJECT_PATH)
        print("STEP 2 OK")

        print("STEP 3: Kapton material...")
        create_kapton(hfss)
        print("STEP 3 OK")

        print("STEP 4: substrate...")
        create_substrate(hfss)
        print("STEP 4 OK")

        print("STEP 5: upper Koch arm...")
        create_arm(hfss, "Koch_Arm_Upper",
                   FEED_GAP / 2.0,
                   FEED_GAP / 2.0 + ARM_LEN)
        print("STEP 5 OK")

        print("STEP 6: lower Koch arm...")
        create_arm(hfss, "Koch_Arm_Lower",
                   -FEED_GAP / 2.0,
                   -(FEED_GAP / 2.0 + ARM_LEN))
        print("STEP 6 OK")

        print("STEP 7: airbox + radiation boundary...")
        airbox = create_airbox(hfss)
        hfss.assign_radiation_boundary_to_objects(airbox)
        print("STEP 7 OK")

        print("STEP 8: lumped port...")
        create_lumped_port(hfss)
        print("STEP 8 OK")

        print("STEP 9: solution setup...")
        create_solution_setup(hfss)
        print("STEP 9 OK")

        print("STEP 10: frequency sweep...")
        create_frequency_sweep(hfss)
        print("STEP 10 OK")

        hfss.save_project()

        print()
        print("=" * 60)
        print("BUILD COMPLETE")
        print("=" * 60)
        print("Project : {}".format(PROJECT_PATH))
        print()
        print("Next steps in HFSS GUI:")
        print("  1. Right-click Setup_UHF -> Analyze")
        print("  2. Right-click Optimetrics -> Sweep_UHF_L -> Analyze")
        print("  3. Create S11 report from Sweep_UHF_L")
        print("  4. Set Y-axis to -30 to 0 dB")
        print()

    except Exception:
        print()
        print("!!! SCRIPT FAILED !!!")
        print("-" * 60)
        traceback.print_exc()
        print("-" * 60)
        if hfss is not None:
            try:
                hfss.save_project()
                print("Partial project saved for inspection.")
            except Exception:
                pass

    input("\nPress ENTER to finish...")


if __name__ == "__main__":
    main()