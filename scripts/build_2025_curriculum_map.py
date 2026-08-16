"""Editorial curriculum mapping for the 2025 VCE Physics exam against the
official VCE Physics Study Design 2024-2027 (data/curriculum/study-design-
2024-2027.json). Every mapping below was made by reading each question's
actual text (extracted directly from current-design-2024-2027/2025-physics-
exam.pdf) against the study design's own key knowledge dot points -- see
scripts/extract_2025_report.py's sibling raw text dump for the source
material. This is deliberately a plain Python literal (not hand-typed JSON)
so interactionId typos fail loudly (KeyError) rather than silently producing
an unmapped question.

Output: data/curriculum/2025-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2025-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 3", "U3AoS1", "Newton's second law along a straight line", ["forces along a line", "Newton's second law"], "high"),
    ("A2", "Unit 3", "U3AoS1", "Uniform circular motion in a vertical plane", ["circular motion", "centripetal acceleration direction"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Conservation of momentum in collisions", ["conservation of momentum", "elastic/inelastic collisions"], "high"),
    ("A4", "Unit 3", "U3AoS1", "Energy transformations in a spring-mass oscillator", ["elastic potential energy", "gravitational potential energy", "conservation of energy"], "high"),
    ("A5", "Unit 3", "U3AoS2", "Field diagrams: gravitational vs electric fields", ["field shapes and directions", "attractive vs repulsive fields"], "high"),
    ("A6", "Unit 3", "U3AoS2", "Force on a current loop from a nearby current-carrying wire", ["magnetic fields of current-carrying wires", "force on a current-carrying conductor"], "high"),
    ("A7", "Unit 3", "U3AoS2", "Static vs non-uniform field definitions", ["static vs changing fields", "uniform vs non-uniform fields"], "high"),
    ("A8", "Unit 3", "U3AoS2", "Electric field between two point charges", ["inverse square law for electric fields", "field superposition"], "high"),
    ("A9", "Unit 3", "U3AoS1", "Work done by a force perpendicular to circular motion", ["work done by a force", "circular motion of a satellite"], "medium"),
    ("A10", "Unit 3", "U3AoS3", "Ideal transformer power/current relationship", ["ideal transformer action", "RMS voltage and current"], "high"),
    ("A11", "Unit 3", "U3AoS3", "Comparing AC RMS and DC supplies", ["root-mean-square (RMS) voltage and current"], "high"),
    ("A12", "Unit 3", "U3AoS3", "Reading frequency/period from an AC voltage trace", ["sinusoidal AC voltage: frequency and period"], "high"),
    ("A13", "Unit 3", "U3AoS2", "Factors affecting DC motor torque", ["simple DC motors", "torque of a motor"], "high"),
    ("A14", "Unit 4", "U4AoS1", "Identifying inertial frames of reference", ["Einstein's postulates of special relativity", "inertial frames"], "high"),
    ("A15", "Unit 4", "U4AoS1", "Electron and X-ray diffraction pattern comparison", ["de Broglie wavelength", "electron diffraction"], "high"),
    ("A16", "Unit 4", "U4AoS1", "Length contraction via the Lorentz factor", ["length contraction", "proper length"], "high"),
    ("A17", "Unit 4", "U4AoS1", "Phenomena requiring the concept of quantisation", ["quantisation", "the photoelectric effect"], "high"),
    ("A18", "Unit 4", "U4AoS2", "Classifying systematic vs random measurement error", ["error and uncertainty"], "high"),
    ("A19", "Unit 4", "U4AoS2", "Identifying a systematic error from an unexpected graph shape", ["identify limitations of data and methods", "systematic error"], "high"),
    ("A20", "Unit 4", "U4AoS2", "Linearising kinematics data (v² vs s)", ["physical significance of the gradient of linearised data"], "high"),

    # ---- Section B ----
    ("B1a", "Unit 3", "U3AoS1", "Free fall: time to fall a known height", ["equations for constant acceleration"], "high"),
    ("B1b", "Unit 3", "U3AoS1", "Free fall: speed just before impact", ["equations for constant acceleration"], "high"),
    ("B1c", "Unit 3", "U3AoS1", "Energy dissipation in an inelastic bounce", ["energy dissipated as heat, sound and deformation"], "high"),
    ("B1d", "Unit 3", "U3AoS1", "Projectile motion: independence of horizontal and vertical components", ["projectile motion near Earth's surface"], "high"),
    ("B2a", "Unit 3", "U3AoS1", "Impulse from a change in momentum", ["impulse: FΔt = mΔv"], "high"),
    ("B2b", "Unit 3", "U3AoS1", "Impulse and average force over an extended collision time", ["impulse: FΔt = mΔv"], "high"),
    ("B2c", "Unit 3", "U3AoS1", "Peak force from a force-displacement graph", ["work done = area under force vs distance graph"], "high"),
    ("B3a", "Unit 3", "U3AoS1", "Free-body force diagram on an inclined plane", ["coplanar forces in two dimensions"], "high"),
    ("B3b", "Unit 3", "U3AoS1", "Resistive force on an incline at constant velocity", ["Newton's laws of motion", "forces along a line"], "high"),
    ("B3c", "Unit 3", "U3AoS1", "Stopping distance from kinetic energy and a resistive force", ["work-energy theorem", "conservation of energy"], "high"),
    ("B4a", "Unit 3", "U3AoS1", "Centripetal force for a car cornering on a flat road", ["uniform circular motion: a vehicle moving around a circular road"], "high"),
    ("B4b", "Unit 3", "U3AoS1", "Banking angle for zero sideways friction", ["uniform circular motion: a vehicle moving around a banked track"], "high"),
    ("B5a", "Unit 3", "U3AoS2", "Electric field magnitude from a single point charge", ["inverse square law for electric fields about a point charge"], "high"),
    ("B5b", "Unit 3", "U3AoS2", "Superposition of electric fields from two point charges", ["field shapes and directions", "vector addition of fields"], "high"),
    ("B6a", "Unit 3", "U3AoS2", "Electric force on a charge in a uniform field", ["magnitude of the force on a charged particle: F = qE"], "high"),
    ("B6b", "Unit 3", "U3AoS2", "Effect of plate separation on an accelerated charge's kinetic energy", ["potential energy changes in a uniform electric field: W = qV"], "high"),
    ("B7a", "Unit 3", "U3AoS2", "Direction of magnetic force on a moving charge", ["magnitude and direction of the force on an electron beam by a magnetic field"], "high"),
    ("B7b", "Unit 3", "U3AoS2", "Radius of a charged particle's circular path in a magnetic field", ["radius of the path followed by an electron in a magnetic field"], "high"),
    ("B8a", "Unit 3", "U3AoS1", "Orbital period of a satellite in uniform circular motion", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B8b", "Unit 3", "U3AoS2", "Gravitational force on an orbiting satellite", ["inverse square law for gravitational fields"], "high"),
    ("B8c", "Unit 3", "U3AoS2", "Explaining centripetal acceleration via Newton's laws and gravity", ["force due to gravity in relation to satellites in orbit"], "high"),
    ("B9", "Unit 3", "U3AoS1", "Limitation of Eg = mgΔh over large altitude changes", ["gravitational potential energy: Eg = mgΔh", "assumption of uniform field"], "medium"),
    ("B10a", "Unit 3", "U3AoS3", "Explaining induced current from a changing magnetic flux", ["electromagnetic induction and induced emf"], "high"),
    ("B10b", "Unit 3", "U3AoS3", "Asymmetric induced EMF spikes from varying rate of flux change", ["rate of change of magnetic flux"], "high"),
    ("B11a", "Unit 3", "U3AoS3", "Current through a load given power and voltage", ["transmission of electricity: power calculations"], "high"),
    ("B11b", "Unit 3", "U3AoS3", "Number of parallel loads from total current and voltage", ["transmission of electricity: power calculations"], "high"),
    ("B11ci", "Unit 3", "U3AoS3", "Identifying step-up vs step-down transformers", ["ideal transformer action"], "high"),
    ("B11cii", "Unit 3", "U3AoS3", "Justifying transformer choice to reduce transmission losses", ["transmission losses across transmission lines", "ideal transformer action"], "high"),
    ("B12a", "Unit 3", "U3AoS3", "Why flux through a rotating coil changes", ["magnetic flux: effect of differing angles between area and field"], "high"),
    ("B12b", "Unit 3", "U3AoS3", "Calculating a change in magnetic flux", ["magnetic flux calculation"], "high"),
    ("B12c", "Unit 3", "U3AoS3", "Average induced EMF from a changing flux over time", ["induced emf: rate of change of magnetic flux"], "high"),
    ("B12d", "Unit 3", "U3AoS3", "Modifying a generator to produce a DC output", ["DC generators (split-ring commutator) vs AC alternators (slip rings)"], "high"),
    ("B13", "Unit 4", "U4AoS1", "Accelerating voltage for a target de Broglie wavelength", ["de Broglie wavelength"], "high"),
    ("B14", "Unit 4", "U4AoS1", "Michelson-Morley's null result and special relativity", ["the Michelson-Morley experiment"], "high"),
    ("B15a", "Unit 4", "U4AoS1", "Slit separation from a double-slit interference pattern", ["Young's double slit experiment: effect of wavelength, distance and slit separation"], "high"),
    ("B15b", "Unit 4", "U4AoS1", "Effect of light frequency on an interference pattern", ["Young's double slit experiment"], "high"),
    ("B16a", "Unit 4", "U4AoS1", "Planck's constant from a photoelectric-effect graph gradient", ["kinetic energy of emitted photoelectrons vs frequency"], "high"),
    ("B16b", "Unit 4", "U4AoS1", "Work function from a photoelectric-effect graph intercept", ["kinetic energy of emitted photoelectrons vs frequency"], "high"),
    ("B17", "Unit 4", "U4AoS1", "Relative speed from a proper-time / dilated-time comparison", ["time dilation", "proper time"], "high"),
    ("B18a", "Unit 4", "U4AoS1", "Photon wavelength from emitted energy", ["photon energy from spectral transitions: E = hf"], "high"),
    ("B18b", "Unit 4", "U4AoS1", "Representing an energy-level transition on a diagram", ["atomic emission line spectra", "electron energy states"], "high"),
    ("B19a", "Unit 4", "U4AoS2", "Classifying independent, dependent and controlled variables", ["independent, dependent and controlled variables"], "high"),
    ("B19b", "Unit 3", "U3AoS2", "Forces on the sides of a current loop parallel to a magnetic field", ["force on a current-carrying conductor: F = nIlB"], "medium"),
    ("B19c", "Unit 4", "U4AoS2", "Justifying an experimental design choice (pivot at the centre)", ["investigation design", "validity of method"], "medium"),
    ("B19d", "Unit 4", "U4AoS2", "Importance of repeated measurements", ["repeatability, reproducibility"], "high"),
    ("B19e", "Unit 4", "U4AoS2", "Plotting data with uncertainty bars and a trend line", ["use of uncertainty bars", "linearised data"], "high"),
    ("B19f", "Unit 4", "U4AoS2", "Gradient of a linearised experimental graph", ["physical significance of the gradient of linearised data"], "high"),
    ("B19gi", "Unit 3", "U3AoS2", "Estimating magnetic field strength from a force-current gradient", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B19gii", "Unit 3", "U3AoS2", "Effect of conductor length on magnetic force", ["force on a current-carrying conductor: F = nIlB"], "high"),
]

YEAR = "2025"


def main():
    interactions = json.loads((ROOT / "data" / f"{YEAR}-interactions.json").read_text(encoding="utf-8-sig"))
    all_ids = {item["id"] for item in interactions}
    mapped_ids = {row[0] for row in MAPPING}

    missing = sorted(all_ids - mapped_ids)
    extra = sorted(mapped_ids - all_ids)
    if missing:
        raise SystemExit(f"Missing curriculum mapping for interaction ids: {missing}")
    if extra:
        raise SystemExit(f"Curriculum mapping references non-existent interaction ids: {extra}")

    questions = []
    for interaction_id, unit, aos, topic, skills, confidence in MAPPING:
        questions.append(
            {
                "canonicalId": f"{YEAR}-{interaction_id}",
                "interactionId": interaction_id,
                "unit": unit,
                "areaOfStudy": aos,
                "topic": topic,
                "skills": skills,
                "confidence": confidence,
                "uncertain": confidence != "high",
            }
        )

    output = {
        "studyDesignRef": "data/curriculum/study-design-2024-2027.json",
        "paperId": YEAR,
        "generatedBy": "editorial mapping — each question's own text checked against the official study design's key knowledge (see scripts/build_2025_curriculum_map.py)",
        "questions": questions,
    }

    OUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(questions)} mapped questions to {OUT_PATH.relative_to(ROOT)}")
    by_aos = {}
    for row in MAPPING:
        by_aos[row[2]] = by_aos.get(row[2], 0) + 1
    for aos, count in sorted(by_aos.items()):
        print(f"  {aos}: {count}")


if __name__ == "__main__":
    main()
