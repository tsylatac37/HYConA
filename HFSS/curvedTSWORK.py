# ============================================================
# DUAL-BAND KOCH FRACTAL DIPOLE — SPHERICAL PATCH + RF SHIELD
# Based on working spherical-patch reference. Minimal changes.
# ============================================================

import os
import math
from ansys.aedt.core import Hfss, settings

os.environ["PYAEDT_USE_PRE_GRPC_ARGS"] = "True"
settings.grpc_secure_mode = False

# --- USER PARAMETERS ---
PROJECT_PATH = r"C:\Users\User\Desktop\SIH\DualBand_Koch_Fractal_Patch.aedt"
AEDT_VERSION = "2025.2"
F_UHF, F_L = 0.43, 1.40
EPS_R, TAND = 3.4, 0.002
H_SUB, TCU = 0.30, 0.035
ARM_LEN, FEED_GAP = 126.0, 2.0
TRACE_WIDTH, KOCH_ITER = 1.5, 1

# --- SPHERICAL PATCH GEOMETRY ---
R_HELMET       = 100.0
AIR_CLEARANCE  = 70.0

# --- RF SHIELD (new) ---
SHIELD_ON        = False        # <-- flip to True for shielded run
SHIELD_GAP       = 15.0         # mm between substrate and shield
SHIELD_THICKNESS = 0.2          # mm

SWEEP_START, SWEEP_STOP, NUM_POINTS = 0.3, 1.6, 131


# ------------------------------------------------------------
# KOCH GENERATOR
# ------------------------------------------------------------
def koch_segment(p1, p2, iteration):
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
    a = math.radians(60.0)
    px = pA[0] + vx * math.cos(a) - vy * math.sin(a)
    py = pA[1] + vx * math.sin(a) + vy * math.cos(a)
    pPeak = (px, py)
    return (koch_segment(p1, pA, iteration - 1)[:-1] +
            koch_segment(pA, pPeak, iteration - 1)[:-1] +
            koch_segment(pPeak, pB, iteration - 1)[:-1] +
            koch_segment(pB, p2, iteration - 1))


# ------------------------------------------------------------
# SPHERICAL PROJECTION (unchanged)
# ------------------------------------------------------------
def planar_to_sphere(x, y, R):
    phi   = y / R
    theta = math.pi / 2.0 + x / R
    s = math.sin(theta)
    return (R * s * math.cos(phi),
            R * s * math.sin(phi),
            R * math.cos(theta))


# ------------------------------------------------------------
# MATERIALS
# ------------------------------------------------------------
def create_kapton(hfss):
    mats = hfss.materials
    if "Kapton_Custom" not in mats.material_keys:
        m = mats.add_material("Kapton_Custom")
        m.permittivity = EPS_R
        m.dielectric_loss_tangent = TAND
        print("   Created Kapton_Custom material")


# ------------------------------------------------------------
# GEOMETRY
# ------------------------------------------------------------
def _trim_to_patch(hfss, obj_name, scale=1.0):
    """Trim a spherical shell to the same front-patch region used for the substrate."""
    x0 =  0.35 * R_HELMET * scale
    y0 = -0.95 * R_HELMET * scale
    z0 = -0.55 * R_HELMET * scale
    x1 = x0 + 0.70 * R_HELMET * scale
    y1 = y0 + 1.90 * R_HELMET * scale
    z1 = z0 + 1.10 * R_HELMET * scale
    pad = 0.5 * R_HELMET
    X0, Y0, Z0 = x0 - pad, y0 - pad, z0 - pad
    X1, Y1, Z1 = x1 + pad, y1 + pad, z1 + pad

    slabs = [
        ([X0, Y0, Z0], [x0 - X0,   Y1 - Y0, Z1 - Z0], obj_name + "_xmin"),
        ([x1, Y0, Z0], [X1 - x1,   Y1 - Y0, Z1 - Z0], obj_name + "_xmax"),
        ([x0, Y0, Z0], [x1 - x0,   y0 - Y0, Z1 - Z0], obj_name + "_ymin"),
        ([x0, y1, Z0], [x1 - x0,   Y1 - y1, Z1 - Z0], obj_name + "_ymax"),
        ([x0, y0, Z0], [x1 - x0,   y1 - y0, z0 - Z0], obj_name + "_zmin"),
        ([x0, y0, z1], [x1 - x0,   y1 - y0, Z1 - z1], obj_name + "_zmax"),
    ]
    names = []
    for origin, sizes, nm in slabs:
        hfss.modeler.create_box(origin=origin, sizes=sizes, name=nm)
        names.append(nm)
    hfss.modeler.subtract(blank_list=[obj_name],
                          tool_list=names,
                          keep_originals=False)


def create_substrate(hfss):
    hfss.modeler.create_sphere(origin=[0, 0, 0], radius=R_HELMET,
                               name="Helmet_Outer", material="Kapton_Custom")
    hfss.modeler.create_sphere(origin=[0, 0, 0], radius=R_HELMET - H_SUB,
                               name="Helmet_Inner")
    hfss.modeler.subtract(blank_list=["Helmet_Outer"],
                          tool_list=["Helmet_Inner"],
                          keep_originals=False)
    shell = hfss.modeler.get_object_from_name("Helmet_Outer")
    shell.name = "Helmet_Substrate"
    _trim_to_patch(hfss, "Helmet_Substrate")

    # kill back-half safety
    hfss.modeler.create_box(
        origin=[-2 * R_HELMET, -2 * R_HELMET, -2 * R_HELMET],
        sizes=[2 * R_HELMET + 0.35 * R_HELMET, 4 * R_HELMET, 4 * R_HELMET],
        name="Kill_Left")
    hfss.modeler.subtract(blank_list=["Helmet_Substrate"],
                          tool_list=["Kill_Left"],
                          keep_originals=False)
    print("   Front doubly-curved Kapton patch created (R={} mm)".format(R_HELMET))


def create_arm(hfss, arm_name, y_start, y_end):
    pts_2d = koch_segment((0.0, y_start), (0.0, y_end), KOCH_ITER)
    R_arm = R_HELMET + TCU / 2.0
    poly_3d = [list(planar_to_sphere(x, y, R_arm)) for (x, y) in pts_2d]
    return hfss.modeler.create_polyline(
        points=poly_3d, name=arm_name, material="copper",
        xsection_type="Rectangle",
        xsection_width=TRACE_WIDTH, xsection_height=TCU)


def carve_grooves(hfss):
    hfss.modeler.subtract(
        blank_list=["Helmet_Substrate"],
        tool_list=["Koch_Arm_Upper", "Koch_Arm_Lower"],
        keep_originals=True)
    print("   Grooves carved into shell")


def create_airbox(hfss):
    return hfss.modeler.create_sphere(
        origin=[0, 0, 0], radius=R_HELMET + 50.0,
        name="AirBox", material="air")


def create_rf_shield(hfss):
    """Thin PEC spherical patch at R_HELMET - SHIELD_GAP, same extent as substrate."""
    R_sh = R_HELMET - SHIELD_GAP
    hfss.modeler.create_sphere(origin=[0, 0, 0], radius=R_sh,
                               name="Shield_Outer", material="pec")
    hfss.modeler.create_sphere(origin=[0, 0, 0], radius=R_sh - SHIELD_THICKNESS,
                               name="Shield_Inner")
    hfss.modeler.subtract(blank_list=["Shield_Outer"],
                          tool_list=["Shield_Inner"],
                          keep_originals=False)
    shield = hfss.modeler.get_object_from_name("Shield_Outer")
    shield.name = "RF_Shield"
    _trim_to_patch(hfss, "RF_Shield", scale=1.05)

    # kill back-half
    hfss.modeler.create_box(
        origin=[-2 * R_HELMET, -2 * R_HELMET, -2 * R_HELMET],
        sizes=[2 * R_HELMET + 0.35 * R_HELMET, 4 * R_HELMET, 4 * R_HELMET],
        name="Shield_Kill_Left")
    hfss.modeler.subtract(blank_list=["RF_Shield"],
                          tool_list=["Shield_Kill_Left"],
                          keep_originals=False)
    print("   RF shield created at R={} mm (gap {} mm)".format(R_sh, SHIELD_GAP))


def create_lumped_port(hfss):
    port_width = TRACE_WIDTH * 3.0
    x_port = R_HELMET + TCU / 2.0
    sheet = hfss.modeler.create_rectangle(
        orientation="YZ",
        origin=[x_port, -port_width / 2.0, -FEED_GAP / 2.0],
        sizes=[port_width, FEED_GAP],
        name="Lumped_Port")
    hfss.lumped_port(
        assignment=sheet.name,
        integration_line=[
            [x_port, 0, -FEED_GAP / 2.0],
            [x_port, 0,  FEED_GAP / 2.0]],
        impedance=50, name="Port1")
    print("   50-ohm lumped port created at (R,0,0)")


# ------------------------------------------------------------
# SETUPS
# ------------------------------------------------------------
def create_solution_setup(hfss):
    s = hfss.create_setup(name="Setup_UHF")
    s.props["Frequency"]     = "{}GHz".format(F_UHF)
    s.props["MaximumPasses"] = 6
    s.props["MaximumDeltaS"] = 0.05
    s.props["MinimumPasses"] = 5
    s.update()
    print("   Adaptive setup created ({} GHz)".format(F_UHF))


def create_frequency_sweep(hfss):
    hfss.create_linear_count_sweep(
        setup="Setup_UHF", unit="GHz",
        start_frequency=SWEEP_START, stop_frequency=SWEEP_STOP,
        num_of_freq_points=NUM_POINTS,
        name="Sweep_UHF_L", save_fields=False)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    import traceback
    print("=" * 60)
    print("DUAL-BAND KOCH DIPOLE — CONFORMAL + SHIELD")
    print("Shield: {}".format("ON (gap {} mm)".format(SHIELD_GAP) if SHIELD_ON else "OFF"))
    print("=" * 60)

    hfss = None
    try:
        hfss = Hfss(version=AEDT_VERSION, non_graphical=False,
                    new_desktop=True, student_version=True,
                    close_on_exit=False, remove_lock=True)
        hfss.solution_type = "DrivenModal"
        hfss.modeler.model_units = "mm"
        hfss.save_project(PROJECT_PATH)

        create_kapton(hfss)
        create_substrate(hfss)

        print("Creating upper Koch arm...")
        create_arm(hfss, "Koch_Arm_Upper",
                   FEED_GAP / 2.0, FEED_GAP / 2.0 + ARM_LEN)
        print("Creating lower Koch arm...")
        create_arm(hfss, "Koch_Arm_Lower",
                   -FEED_GAP / 2.0, -(FEED_GAP / 2.0 + ARM_LEN))

        carve_grooves(hfss)

        if SHIELD_ON:
            create_rf_shield(hfss)

        print("Creating airbox & radiation boundary...")
        air = create_airbox(hfss)
        hfss.assign_radiation_boundary_to_objects(air)

        print("Creating lumped port...")
        create_lumped_port(hfss)

        create_solution_setup(hfss)
        create_frequency_sweep(hfss)
        hfss.save_project()

        print("\n" + "=" * 60)
        print("BUILD COMPLETE ->", PROJECT_PATH)
        print("=" * 60)

    except Exception:
        print("\n!!! SCRIPT FAILED !!!")
        traceback.print_exc()
        if hfss is not None:
            try: hfss.save_project()
            except Exception: pass

    input("\nPress ENTER to finish...")


if __name__ == "__main__":
    main()