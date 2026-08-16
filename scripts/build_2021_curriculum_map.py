"""Editorial curriculum mapping for the 2021 VCE Physics exam against the
official VCE Physics Study Design 2017-2023 (data/curriculum/study-design-
2016.json). Every mapping below was made by reading each question's actual
text (extracted directly from previous-design-2017-2023/2021-physics-
exam.pdf) against the study design's own key knowledge dot points. This is
deliberately a plain Python literal (not hand-typed JSON) so interactionId
typos fail loudly (KeyError) rather than silently producing an unmapped
question. See scripts/build_2023_curriculum_map.py for the sibling script
this mirrors.

Output: data/curriculum/2021-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2021-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 4", "U4AoS3", "Identifying a 'precise but inaccurate' set of dart throws", ["precision, accuracy, reliability and validity of data"], "high"),
    ("A2", "Unit 3", "U3AoS1", "Identifying charge signs from an electric field line diagram", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Electric field strength vs position graph between charged parallel plates", ["potential energy changes in a uniform electric field: W = qV, E = V/d"], "high"),
    ("A4", "Unit 3", "U3AoS1", "Radius of a planet from its surface gravity and mass", ["gravitational field and gravitational force concepts"], "high"),
    ("A5", "Unit 3", "U3AoS2", "Direction of rotation of a stationary DC motor coil when switched on", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("A6", "Unit 3", "U3AoS2", "Time interval for a given change in magnetic flux and induced EMF", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("A7", "Unit 3", "U3AoS2", "Mains current drawn by a step-down phone charger transformer", ["ideal transformer action"], "high"),
    ("A8", "Unit 3", "U3AoS2", "Function of a split-ring commutator in a simple generator", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("A9", "Unit 3", "U3AoS3", "Expression for horizontal distance travelled by a runner leaving a platform", ["motion of projectiles near Earth's surface"], "high"),
    ("A10", "Unit 3", "U3AoS3", "Time taken to fall from a diving platform to the water", ["motion of projectiles near Earth's surface"], "high"),
    ("A11", "Unit 3", "U3AoS3", "Spring constant from a force-compression graph", ["strain potential energy: ideal springs obeying Hooke's Law"], "high"),
    ("A12", "Unit 3", "U3AoS3", "Potential energy stored in a compressed spring", ["strain potential energy: area under a force-distance graph"], "high"),
    ("A13", "Unit 4", "U4AoS1", "Amplitude and frequency of a travelling wave from its waveform and speed", ["identify the amplitude, wavelength, period and frequency of waves"], "high"),
    ("A14", "Unit 4", "U4AoS1", "Matching electromagnetic spectrum regions to real-world applications", ["compare the wavelength and frequencies of different regions of the electromagnetic spectrum ... distinct uses"], "high"),
    ("A15", "Unit 4", "U4AoS1", "Diagram showing correct dispersion of white light through a prism", ["investigate and explain theoretically and practically colour dispersion in prisms and lenses"], "high"),
    ("A16", "Unit 4", "U4AoS2", "Measurement essential to finding maximum photoelectron kinetic energy", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("A17", "Unit 4", "U4AoS2", "De Broglie wavelength of an everyday-scale moving object", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("A18", "Unit 4", "U4AoS2", "Power of a light source from its photon emission rate", ["interpret spectra and calculate the energy of absorbed or emitted photons: delta E = hf"], "high"),
    ("A19", "Unit 4", "U4AoS2", "Number of whole wavelengths in a de Broglie standing-wave orbit", ["describe the quantised states of the atom with reference to electrons forming standing waves"], "high"),
    ("A20", "Unit 3", "U3AoS3", "Property of an inertial frame of reference", ["Einstein's postulates of special relativity: inertial (non-accelerated) frames of reference"], "high"),

    # ---- Section B ----
    ("B1a", "Unit 3", "U3AoS1", "Direction of the combined magnetic field of two perpendicular bar magnets", ["field shapes and directions ... dipoles and monopoles"], "high"),
    ("B1b", "Unit 3", "U3AoS1", "Magnitude of a combined magnetic field from two equal sources", ["field shapes and directions"], "high"),
    ("B2a", "Unit 3", "U3AoS1", "Sketching magnetic field lines around a loudspeaker's current-carrying coil", ["magnetic fields of ... current-carrying wires, loops and solenoids"], "high"),
    ("B2b", "Unit 3", "U3AoS1", "Direction of the magnetic force on a current-carrying coil", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B2c", "Unit 3", "U3AoS1", "Magnitude of the magnetic force on a current-carrying coil", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B3", "Unit 3", "U3AoS1", "Mass of a pulsar from a planet's orbital radius and period", ["model satellite motion ... as uniform circular orbital motion", "gravitational field and gravitational force concepts"], "high"),
    ("B4", "Unit 3", "U3AoS3", "Newton's third law reaction force to a person's weight", ["Newton's three laws of motion"], "high"),
    ("B5a", "Unit 3", "U3AoS1", "Why a magnetic field exerts no force on a stationary electron", ["magnetic force on a charged particle: F = qvB"], "high"),
    ("B5b", "Unit 3", "U3AoS1", "Electric force on an electron between charged parallel plates", ["electric field acceleration of a charge: F = qE"], "high"),
    ("B5c", "Unit 3", "U3AoS1", "Evaluating claims about the magnetic force on an accelerating electron", ["magnetic force on a charged particle: F = qvB"], "high"),
    ("B6a", "Unit 3", "U3AoS2", "Sketching an AC generator's output EMF vs time", ["compare sinusoidal AC voltages produced as a result of the uniform rotation of a loop"], "high"),
    ("B6b", "Unit 3", "U3AoS2", "Function of slip rings in an AC generator", ["explain the production of ... AC voltage in alternators, including the use of ... slip rings"], "high"),
    ("B6ci", "Unit 3", "U3AoS2", "Converting an AC generator design into a DC generator", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("B6cii", "Unit 3", "U3AoS2", "Sketching a DC generator's output EMF vs time", ["explain the production of DC voltage in DC generators"], "high"),
    ("B7a", "Unit 3", "U3AoS2", "Why voltage is stepped up for long-distance transmission", ["identify the advantage of the use of AC power as a domestic power supply", "transmission losses"], "high"),
    ("B7b", "Unit 3", "U3AoS2", "Current in high-voltage overhead transmission lines", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B7c", "Unit 3", "U3AoS2", "Maximum power available for domestic use after transmission losses", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B8a", "Unit 3", "U3AoS3", "Thrust force on a rocket at launch from its acceleration", ["Newton's three laws of motion"], "high"),
    ("B8b", "Unit 3", "U3AoS3", "Kinetic energy of a descending space capsule", ["kinetic energy at low speeds: Ek = 1/2 m v^2"], "high"),
    ("B8c", "Unit 3", "U3AoS1", "Gravitational potential energy from a non-uniform field-vs-altitude graph", ["the change in gravitational potential energy from area under a force-distance graph and area under a field-distance graph multiplied by mass"], "high"),
    ("B8d", "Unit 3", "U3AoS3", "How a capsule's mechanical energy was transformed and dissipated on descent", ["energy dissipated to the environment (considered as a combination of heat, sound and deformation of material)"], "high"),
    ("B9a", "Unit 3", "U3AoS3", "Speed at the bottom of a loop from conservation of energy", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B9b", "Unit 3", "U3AoS3", "Deriving the critical-speed condition for a vertical circular loop", ["Newton's second law to circular motion in a vertical plane (forces at the highest and lowest positions only)"], "high"),
    ("B9c", "Unit 3", "U3AoS3", "Maximum loop height satisfying the critical-speed condition", ["Newton's second law to circular motion in a vertical plane", "conservation of energy"], "high"),
    ("B9d", "Unit 3", "U3AoS3", "Effect of friction on the required loop radius", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B10a", "Unit 3", "U3AoS3", "Why length contracts but width doesn't for a relativistic spaceship", ["model mathematically ... length contraction"], "high"),
    ("B10b", "Unit 3", "U3AoS3", "Proper length of a spaceship from its contracted length", ["describe proper length (L0)", "length contraction: L = L0/gamma"], "high"),
    ("B11", "Unit 4", "U4AoS1", "Whether light passes through two crossed polarising filters", ["explain polarisation of visible light and its relation to a transverse wave model"], "high"),
    ("B12a", "Unit 4", "U4AoS1", "Angle of incidence at an air-to-fibre-core boundary", ["refraction using Snell's Law"], "high"),
    ("B12b", "Unit 4", "U4AoS1", "Whether light transmits into an optical fibre's cladding", ["total internal reflection and critical angle"], "high"),
    ("B13a", "Unit 4", "U4AoS1", "Spacing of dark interference bands in a double-slit experiment", ["effect of wavelength, distance of screen and slit separation on interference patterns"], "high"),
    ("B13b", "Unit 4", "U4AoS1", "How Young's double-slit experiment supports the wave model of light", ["explain the results of Young's double slit experiment: evidence for the wave-like nature of light"], "high"),
    ("B14a", "Unit 4", "U4AoS1", "Sketching the Doppler-shifted frequency heard as a source passes an observer", ["explain qualitatively the Doppler effect"], "high"),
    ("B14b", "Unit 4", "U4AoS1", "Naming the physics principle behind a passing siren's pitch change", ["explain qualitatively the Doppler effect"], "high"),
    ("B15", "Unit 4", "U4AoS2", "Planck's constant from a measured threshold frequency and work function", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B16", "Unit 4", "U4AoS2", "Which light model rapid low-intensity photoemission supports", ["analyse the photoelectric effect with reference to: evidence for the particle-like nature of light"], "high"),
    ("B17a", "Unit 4", "U4AoS2", "Momentum of a photon from its frequency", ["compare the momentum of photons and of matter of the same wavelength"], "high"),
    ("B17b", "Unit 4", "U4AoS2", "Force exerted by reflecting photons on a space sail", ["compare the momentum of photons and of matter of the same wavelength"], "high"),
    ("B18a", "Unit 4", "U4AoS2", "De Broglie wavelength of electrons from their speed", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("B18b", "Unit 4", "U4AoS2", "Aperture diameter giving electrons the same diffraction spacing as X-rays", ["investigate and describe ... the effects of varying the width of a gap or diameter of an obstacle on the diffraction pattern"], "high"),
    ("B19a", "Unit 4", "U4AoS2", "Identifying an atomic transition matching a given emitted photon wavelength", ["analyse the absorption of photons by atoms ... frequency and wavelength of emitted photons"], "high"),
    ("B19b", "Unit 4", "U4AoS2", "Total number of spectral lines from all possible energy-level transitions", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B20a", "Unit 4", "U4AoS3", "Why repeated time measurements were taken in a centripetal-force experiment", ["precision, accuracy, reliability and validity of data"], "high"),
    ("B20b", "Unit 3", "U3AoS3", "Cause of the tension supplying centripetal force on a whirled stopper", ["uniform circular motion of an object moving in a horizontal plane: an object on the end of a string"], "high"),
    ("B20c", "Unit 3", "U3AoS3", "Deriving an equation for Mg from the centripetal-force relationship", ["uniform circular motion of an object moving in a horizontal plane"], "medium"),
    ("B20d", "Unit 4", "U4AoS3", "Completing a data table of derived quantities from raw measurements", ["methods of organising, analysing and evaluating primary data"], "high"),
    ("B20e", "Unit 4", "U4AoS3", "Plotting linearised data with uncertainty bars and a line of best fit", ["methods of organising, analysing and evaluating primary data ... sources of uncertainty and error"], "high"),
    ("B20f", "Unit 4", "U4AoS3", "Gradient of a linearised experimental graph", ["methods of organising, analysing and evaluating primary data"], "high"),
    ("B20g", "Unit 3", "U3AoS3", "Using a graph's gradient to find the mass of the rubber stopper", ["uniform circular motion of an object moving in a horizontal plane"], "medium"),
]

YEAR = "2021"


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
        "studyDesignRef": "data/curriculum/study-design-2016.json",
        "paperId": YEAR,
        "generatedBy": "editorial mapping — each question's own text checked against the official 2017-2023 study design's key knowledge (see scripts/build_2021_curriculum_map.py)",
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
