"""Editorial curriculum mapping for the 2024 VCE Physics exam against the
official VCE Physics Study Design 2024-2027 (data/curriculum/study-design-
2024-2027.json). Every mapping below was made by reading each question's
actual content directly off the rendered exam pages (2024's exam PDF has no
extractable text layer at all -- every character is a vector path, see
Missing_Resources.md -- so unlike 2025, there is no plain-text dump to check
against; each question's wording below was read from the same 110dpi page
renders used to hand-verify this paper's interaction geometry, not
reconstructed from memory) against the study design's own key knowledge dot
points. This is deliberately a plain Python literal (not hand-typed JSON) so
interactionId typos fail loudly (KeyError) rather than silently producing an
unmapped question. See scripts/build_2025_curriculum_map.py for the sibling
year this mirrors.

Output: data/curriculum/2024-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2024-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 3", "U3AoS1", "Apparent weight in a lift moving at constant velocity", ["Newton's second law", "forces along a line"], "high"),
    ("A2", "Unit 3", "U3AoS1", "Orbital radius change when a satellite's mass changes at constant speed", ["satellite motion modelled as uniform circular motion"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Forces on a conical-pendulum ball seen front-on", ["uniform circular motion (object on a string)", "coplanar forces in two dimensions"], "high"),
    ("A4", "Unit 3", "U3AoS1", "Launch speed from a spring's force-compression graph", ["elastic potential energy and Hooke's Law", "work as area under a force-distance graph", "conservation of energy"], "high"),
    ("A5", "Unit 3", "U3AoS1", "Total mechanical energy of a falling object over time", ["conservation of energy and momentum in one-dimensional isolated systems", "gravitational potential energy"], "high"),
    ("A6", "Unit 3", "U3AoS2", "Field strength at the midpoint between two identical magnets", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles", "magnetic fields of bar magnets"], "high"),
    ("A7", "Unit 3", "U3AoS2", "Force and torque on a current loop rotated 90° in a field", ["force on a current-carrying conductor: F = nIlB", "simple DC motors ... torque"], "high"),
    ("A8", "Unit 3", "U3AoS2", "Force on a current-carrying wire in a uniform magnetic field", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("A9", "Unit 3", "U3AoS2", "New separation of two point charges for a sixfold force increase", ["inverse square law for gravitational and electric fields about a point mass/charge"], "high"),
    ("A10", "Unit 3", "U3AoS3", "Matching an induced-current graph to its magnetic-flux graph", ["electromagnetic induction and induced emf", "magnetic flux"], "high"),
    ("A11", "Unit 3", "U3AoS3", "Reason for high-voltage electricity transmission", ["transmission losses across transmission lines"], "high"),
    ("A12", "Unit 3", "U3AoS3", "Induced current and field direction for a coil moving off a magnet", ["electromagnetic induction and induced emf", "magnetic fields of ... loops and solenoids"], "high"),
    ("A13", "Unit 3", "U3AoS3", "Oscilloscope output of a commutator-based simple generator", ["DC generators (split-ring commutator) vs AC alternators (slip rings)"], "high"),
    ("A14", "Unit 4", "U4AoS1", "Length contraction of a passing observer's window measurements", ["length contraction"], "high"),
    ("A15", "Unit 4", "U4AoS1", "Effect of a much larger Lorentz factor on an electron's speed and energy", ["mass-energy equivalence: E = mc², Etot = Ek + E0", "relativistic examples: ... particle accelerators"], "high"),
    ("A16", "Unit 4", "U4AoS1", "Matching an energy-level transition diagram to a spectral-line pattern", ["atomic absorption and emission line spectra", "photon energy from spectral transitions: E = hf"], "high"),
    ("A17", "Unit 4", "U4AoS1", "Position of a standing wave on a string a short time later", ["standing waves and superposition"], "high"),
    ("A18", "Unit 4", "U4AoS1", "Fringe spacing when slit separation is halved and screen distance doubled", ["Young's double slit experiment and interference"], "high"),
    ("A19", "Unit 3", "U3AoS1", "Identifying the linear graph form of the orbital velocity relationship", ["satellite motion modelled as uniform circular motion"], "medium"),
    ("A20", "Unit 4", "U4AoS2", "Definition of precision in repeated measurements", ["accuracy, precision, repeatability, reproducibility, resolution, validity"], "high"),

    # ---- Section B ----
    ("B1a", "Unit 3", "U3AoS1", "Acceleration of two towed boats from a resistance and tension force", ["Newton's second law", "forces along a line"], "high"),
    ("B1b", "Unit 3", "U3AoS1", "Tension in the second tow rope", ["Newton's second law", "forces along a line"], "high"),
    ("B2a", "Unit 3", "U3AoS1", "Maximum banked-track speed with no sideways friction", ["uniform circular motion (vehicle on a circular/banked road)"], "high"),
    ("B2b", "Unit 3", "U3AoS1", "How the normal force supplies centripetal force on a banked track", ["uniform circular motion (vehicle on a circular/banked road)", "coplanar forces in two dimensions"], "high"),
    ("B3a", "Unit 3", "U3AoS1", "Cliff height from projectile motion given flight time and launch angle", ["projectile motion near Earth's surface"], "high"),
    ("B3b", "Unit 3", "U3AoS1", "Horizontal range of a projectile", ["projectile motion near Earth's surface"], "high"),
    ("B3c", "Unit 3", "U3AoS1", "Qualitative effect of air resistance on a projectile's flight path", ["qualitative effect of air resistance"], "high"),
    ("B4a", "Unit 3", "U3AoS1", "Impulse on a crash-test dummy from a force-time graph", ["impulse: FΔt = mΔv"], "high"),
    ("B4b", "Unit 3", "U3AoS1", "Sketching a lower, longer-duration collision force-time graph", ["impulse: FΔt = mΔv", "work as area under a force-distance graph"], "high"),
    ("B5a", "Unit 3", "U3AoS1", "Change in momentum of a bouncing basketball", ["impulse: FΔt = mΔv", "conservation of momentum"], "high"),
    ("B5b", "Unit 3", "U3AoS1", "Classifying a bounce as elastic or inelastic", ["elastic and inelastic collisions"], "high"),
    ("B6", "Unit 3", "U3AoS2", "Whether gravitational attraction can supply a supply-craft's centripetal force", ["force due to gravity and normal force for satellites in circular orbit", "inverse square law for gravitational ... fields"], "high"),
    ("B7a", "Unit 3", "U3AoS2", "Electron speed after acceleration through a potential difference", ["electric field acceleration of a charge: F = qE, W = qV"], "high"),
    ("B7b", "Unit 3", "U3AoS2", "Accelerating voltage needed for a given electron speed", ["electric field acceleration of a charge: F = qE, W = qV"], "high"),
    ("B7c", "Unit 3", "U3AoS2", "Comparing a proton's and electron's circular path in the same field", ["radius of circular path of a charged particle in a magnetic field", "magnetic force on a charged particle: F = qvB"], "high"),
    ("B8a", "Unit 3", "U3AoS2", "Sketching electric field lines between a thundercloud and the ground", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles"], "high"),
    ("B8b", "Unit 3", "U3AoS2", "Electric field magnitude between two charged parallel-plate-like surfaces", ["electric field acceleration of a charge: F = qE, W = qV"], "high"),
    ("B8c", "Unit 3", "U3AoS2", "Total energy transferred by a lightning discharge", ["potential energy changes of a mass or charge moving in a field"], "medium"),
    ("B9a", "Unit 3", "U3AoS2", "Coil orientation giving zero magnetic force on one side of a DC motor", ["force on a current-carrying conductor: F = nIlB", "simple DC motors"], "high"),
    ("B9b", "Unit 3", "U3AoS2", "Coil orientation where a DC motor will not start to rotate", ["simple DC motors, split-ring commutators, torque"], "high"),
    ("B9c", "Unit 3", "U3AoS2", "Increasing a DC motor's torque with the same coil and battery", ["simple DC motors, split-ring commutators, torque"], "high"),
    ("B10a", "Unit 3", "U3AoS3", "Purpose of slip rings in an AC generator", ["DC generators (split-ring commutator) vs AC alternators (slip rings)"], "high"),
    ("B10b", "Unit 3", "U3AoS3", "Peak-to-peak voltage and frequency from an oscilloscope trace", ["sinusoidal AC voltage: frequency, period, amplitude, peak-to-peak voltage/current"], "high"),
    ("B10c", "Unit 3", "U3AoS3", "Modifying an apparatus to change an induced-emf trace's amplitude and frequency", ["electromagnetic induction and induced emf", "magnetic flux"], "high"),
    ("B11a", "Unit 3", "U3AoS3", "Secondary turns count for a step-down transformer", ["ideal transformer action"], "high"),
    ("B11b", "Unit 3", "U3AoS3", "RMS input current to an ideal transformer", ["ideal transformer action"], "high"),
    ("B11c", "Unit 3", "U3AoS3", "Why a transformer needs AC rather than constant DC input", ["ideal transformer action", "electromagnetic induction and induced emf"], "high"),
    ("B12a", "Unit 3", "U3AoS3", "Maximum output power of a solar PV array", ["photovoltaic cells and the need for an inverter"], "high"),
    ("B12b", "Unit 3", "U3AoS3", "Maximum voltage and current from one series string of PV panels", ["photovoltaic cells and the need for an inverter"], "high"),
    ("B12c", "Unit 3", "U3AoS3", "Maximum voltage and current from the whole parallel-string PV array", ["photovoltaic cells and the need for an inverter"], "high"),
    ("B12d", "Unit 3", "U3AoS3", "Function of the inverter in a solar PV installation", ["photovoltaic cells and the need for an inverter"], "high"),
    ("B13a", "Unit 4", "U4AoS1", "Classical-mechanics travel time for a muon to reach a mountain-top detector", ["relativistic examples: muon decay, particle accelerators, GPS satellite corrections"], "medium"),
    ("B13b", "Unit 4", "U4AoS1", "Whether a muon should survive to reach the detector, per classical mechanics", ["relativistic examples: muon decay"], "high"),
    ("B13c", "Unit 4", "U4AoS1", "Lorentz factor for a muon travelling at 0.985c", ["time dilation and length contraction"], "high"),
    ("B13d", "Unit 4", "U4AoS1", "Muon mean half-life in the physicists' (ground) frame of reference", ["time dilation and length contraction", "proper time and proper length"], "high"),
    ("B13e", "Unit 4", "U4AoS1", "How special relativity explains muons reaching the detector", ["time dilation and length contraction", "relativistic examples: muon decay"], "high"),
    ("B14a", "Unit 4", "U4AoS1", "Total energy released in electron-positron annihilation", ["mass-energy equivalence: E = mc², Etot = Ek + E0"], "high"),
    ("B14b", "Unit 4", "U4AoS1", "Why annihilation gamma rays are emitted in opposite directions", ["momentum of photons and matter"], "medium"),
    ("B15a", "Unit 4", "U4AoS1", "Electron momentum from a given de Broglie wavelength", ["de Broglie wavelength", "momentum of photons and matter"], "high"),
    ("B15b", "Unit 4", "U4AoS1", "Whether a detectable diffraction pattern forms when wavelength < spacing", ["diffraction and the effect of gap/obstacle size", "electron diffraction as evidence for wave-like matter"], "high"),
    ("B15c", "Unit 4", "U4AoS1", "Why electrons and X-rays can produce near-identical diffraction patterns", ["electron diffraction as evidence for wave-like matter", "de Broglie wavelength"], "high"),
    ("B15d", "Unit 4", "U4AoS1", "X-ray photon energy from a diffraction pattern's implied wavelength", ["quantised photon energy: E = hf"], "high"),
    ("B16a", "Unit 4", "U4AoS2", "Classifying an experiment's controlled, dependent and independent variables", ["independent, dependent and controlled variables"], "high"),
    ("B16b", "Unit 4", "U4AoS2", "Plotting photoelectric-effect data with uncertainty bars and a line of best fit", ["error and uncertainty", "use of uncertainty bars"], "high"),
    ("B16ci", "Unit 4", "U4AoS1", "Planck's constant from a stopping-voltage vs frequency graph gradient", ["quantised photon energy: E = hf", "the photoelectric effect"], "high"),
    ("B16cii", "Unit 4", "U4AoS1", "Threshold frequency from a photoelectric-effect graph", ["the photoelectric effect"], "high"),
    ("B16ciii", "Unit 4", "U4AoS1", "Work function of the photocell's metal plate", ["the photoelectric effect"], "high"),
    ("B16d", "Unit 4", "U4AoS1", "What stopping-voltage measurements reveal about emitted photoelectrons", ["the photoelectric effect"], "high"),
    ("B16e", "Unit 4", "U4AoS1", "Effect of a different plate metal on the photoelectric graph", ["the photoelectric effect"], "high"),
    ("B16f", "Unit 4", "U4AoS1", "Effect of switching filters at constant light power on the threshold point", ["the photoelectric effect", "quantised photon energy: E = hf"], "high"),
    ("B16g", "Unit 4", "U4AoS1", "Effect of light frequency on saturation photocurrent at constant power", ["the photoelectric effect"], "high"),
    ("B16h", "Unit 4", "U4AoS1", "A photoelectric-effect result explained by light's particle nature but not its wave nature", ["the photoelectric effect", "limitations of the wave model of light"], "high"),
]

YEAR = "2024"


def main():
    interactions = json.loads((ROOT / "public" / "interactions" / f"{YEAR}.json").read_text(encoding="utf-8-sig"))
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
        "generatedBy": "editorial mapping — each question read directly off the rendered exam pages (no text layer to extract) and checked against the official study design's key knowledge (see scripts/build_2024_curriculum_map.py)",
        "questions": questions,
    }

    OUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(questions)} mapped questions to {OUT_PATH.relative_to(ROOT)}")
    by_aos = {}
    for row in MAPPING:
        by_aos[row[2]] = by_aos.get(row[2], 0) + 1
    for aos, count in sorted(by_aos.items()):
        print(f"  {aos}: {count}")
    medium_or_lower = [row[0] for row in MAPPING if row[5] != "high"]
    if medium_or_lower:
        print(f"  flagged uncertain ({len(medium_or_lower)}): {medium_or_lower}")


if __name__ == "__main__":
    main()
