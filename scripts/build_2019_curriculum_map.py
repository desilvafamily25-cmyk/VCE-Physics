"""Editorial curriculum mapping for the 2019 VCE Physics exam against the
official VCE Physics Study Design 2017-2023 (data/curriculum/study-design-
2016.json). Every mapping below was made by reading each question's actual
text (extracted directly from previous-design-2017-2023/2019-physics-
exam.pdf) against the study design's own key knowledge dot points. This is
deliberately a plain Python literal (not hand-typed JSON) so interactionId
typos fail loudly (KeyError) rather than silently producing an unmapped
question. See scripts/build_2023_curriculum_map.py for the sibling script
this mirrors.

Output: data/curriculum/2019-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2019-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 3", "U3AoS1", "Comparing attraction/repulsion properties of magnetic and gravitational forces", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles"], "high"),
    ("A2", "Unit 3", "U3AoS1", "Voltage between parallel plates from electric field strength and separation", ["potential energy changes in a uniform electric field: W = qV, E = V/d"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Direction of the net electric force on a charge from two others", ["inverse square law for gravitational and electric fields about a point mass/charge"], "high"),
    ("A4", "Unit 3", "U3AoS1", "Surface gravity of a planet with double mass and half radius", ["gravitational field and gravitational force concepts"], "high"),
    ("A5", "Unit 3", "U3AoS2", "Identifying transformer coils and step-up/step-down function", ["ideal transformer action"], "high"),
    ("A6", "Unit 3", "U3AoS2", "RMS current in a transformer's primary circuit", ["ideal transformer action"], "high"),
    ("A7", "Unit 3", "U3AoS2", "AC generator output-voltage trace at a different rotation rate", ["sinusoidal AC voltage: frequency, period, amplitude, peak-to-peak voltage/current"], "high"),
    ("A8", "Unit 3", "U3AoS2", "Relating a generator's voltage and magnetic-flux graphs", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("A9", "Unit 4", "U4AoS1", "Relative light speeds in three media from a refraction diagram", ["refraction using Snell's Law"], "high"),
    ("A10", "Unit 4", "U4AoS1", "Minimum refractive index for light to cross a glass-liquid boundary", ["total internal reflection and critical angle"], "high"),
    ("A11", "Unit 3", "U3AoS3", "Thrust force on a plane flying at constant velocity", ["Newton's three laws of motion: forces along a line"], "high"),
    ("A12", "Unit 3", "U3AoS3", "Motion of a ball undergoing projectile motion off a table", ["motion of projectiles near Earth's surface"], "high"),
    ("A13", "Unit 3", "U3AoS3", "Proper length of a spaceship from its measured contracted length", ["model mathematically time dilation and length contraction"], "high"),
    ("A14", "Unit 4", "U4AoS2", "De Broglie wavelength of accelerated electrons", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("A15", "Unit 4", "U4AoS2", "Effect of doubling electron speed on a diffraction pattern's fringe spacing", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("A16", "Unit 4", "U4AoS2", "Effect of increased light intensity on photoelectron kinetic energy", ["effects of intensity of incident irradiation on the emission of photoelectrons"], "high"),
    ("A17", "Unit 4", "U4AoS2", "Comparing coherence of laser and incandescent light", ["compare the production of light in lasers, synchrotrons, LEDs and incandescent lights"], "high"),
    ("A18", "Unit 4", "U4AoS3", "Identifying variables in a pendulum-based gravity investigation", ["independent, dependent and controlled variables"], "high"),
    ("A19", "Unit 4", "U4AoS3", "Why timing five oscillations reduces measurement uncertainty", ["precision, accuracy, reliability and validity of data"], "high"),
    ("A20", "Unit 3", "U3AoS3", "Identifying the correct physics of crumple-zone energy absorption", ["energy dissipated to the environment (considered as a combination of heat, sound and deformation of material)"], "high"),

    # ---- Section B ----
    ("B1a", "Unit 3", "U3AoS1", "Sign of a charge from its circular deflection in a magnetic field", ["magnetic force on a charged particle: F = qvB"], "high"),
    ("B1b", "Unit 3", "U3AoS1", "Why a charged particle follows a circular arc in a magnetic field", ["magnetic force on a charged particle: F = qvB"], "high"),
    ("B2", "Unit 3", "U3AoS1", "Sketching electric field lines between two equal positive charges", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles"], "high"),
    ("B3a", "Unit 3", "U3AoS2", "Identifying the positive commutator terminal in a DC motor", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("B3b", "Unit 3", "U3AoS1", "Direction of the magnetic force on a current-carrying motor coil side", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B3c", "Unit 3", "U3AoS2", "Role of the commutator in a DC motor's operation", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("B3d", "Unit 3", "U3AoS1", "Magnitude of the magnetic force on a current-carrying motor coil side", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B4a", "Unit 3", "U3AoS1", "Gravitational field strength at Earth's surface from a field-vs-distance graph", ["gravitational field and gravitational force concepts"], "high"),
    ("B4b", "Unit 3", "U3AoS1", "Why gravitational field strength is zero at Earth's centre", ["gravitational field and gravitational force concepts"], "high"),
    ("B4c", "Unit 3", "U3AoS1", "Potential energy gained moving from Earth's centre to its surface", ["the change in gravitational potential energy from area under a force-distance graph and area under a field-distance graph multiplied by mass"], "high"),
    ("B5a", "Unit 3", "U3AoS1", "Forces acting on an orbiting GPS satellite", ["force due to gravity and normal reaction force ... satellites in orbit"], "high"),
    ("B5b", "Unit 3", "U3AoS1", "Orbital period of a GPS satellite", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B6a", "Unit 3", "U3AoS2", "Power drawn by a low-voltage lighting system", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B6b", "Unit 3", "U3AoS2", "Why lights are dimmer than expected due to cable resistance", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B6c", "Unit 3", "U3AoS2", "Changes to improve lighting brightness given transmission losses", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B7a", "Unit 3", "U3AoS2", "Identifying a piece of equipment as an alternator, generator or motor", ["explain the production of DC voltage in DC generators and AC voltage in alternators"], "high"),
    ("B7bi", "Unit 3", "U3AoS2", "Magnetic flux through a loop at a given orientation", ["magnetic flux: Phi = B*A"], "high"),
    ("B7bii", "Unit 3", "U3AoS2", "Explaining a magnetic flux value from loop orientation", ["magnetic flux: Phi = B*A", "qualitative effect of differing angles"], "high"),
    ("B7c", "Unit 3", "U3AoS2", "Period of rotation from a generator's rotation frequency", ["sinusoidal AC voltage: frequency, period"], "high"),
    ("B7d", "Unit 3", "U3AoS2", "Maximum magnetic flux through a rotating loop", ["magnetic flux: Phi = B*A"], "high"),
    ("B7e", "Unit 3", "U3AoS2", "Average voltage over the first quarter turn of a rotating loop", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("B7f", "Unit 3", "U3AoS2", "Ways to increase a generator's output voltage amplitude", ["generation of emf ... rate of change of magnetic flux", "number of loops"], "high"),
    ("B7g", "Unit 3", "U3AoS2", "Sketching a DC generator's output after adding a split-ring commutator", ["explain the production of DC voltage in DC generators"], "high"),
    ("B8a", "Unit 3", "U3AoS3", "Height of a loop-the-loop track from energy conservation", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B8b", "Unit 3", "U3AoS3", "Normal reaction force on a car at the top of a vertical loop", ["Newton's second law to circular motion in a vertical plane"], "high"),
    ("B8c", "Unit 3", "U3AoS3", "Why a car doesn't fall off the track at the top of a loop", ["Newton's second law to circular motion in a vertical plane"], "high"),
    ("B9", "Unit 3", "U3AoS3", "Proton speed before a head-on collision from momentum conservation", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B10a", "Unit 3", "U3AoS3", "Time of flight to a projectile's highest point", ["motion of projectiles near Earth's surface"], "high"),
    ("B10b", "Unit 3", "U3AoS3", "Range of a projectile launched at an angle", ["motion of projectiles near Earth's surface"], "high"),
    ("B11", "Unit 3", "U3AoS3", "Einstein's second postulate of special relativity", ["describe Einstein's two postulates for his theory of special relativity"], "high"),
    ("B12", "Unit 4", "U4AoS1", "Wave speed from wavelength and the time to move to zero displacement", ["wave speed, frequency, wavelength and period: v = f*lambda"], "high"),
    ("B13a", "Unit 4", "U4AoS1", "Wavelength of a transverse wave from its speed and frequency", ["wave speed, frequency, wavelength and period"], "high"),
    ("B13b", "Unit 4", "U4AoS1", "Whether a standing wave forms on a fixed string at a given frequency", ["standing waves in strings fixed at one or both ends"], "high"),
    ("B14a", "Unit 4", "U4AoS1", "Frequency of microwaves from a double-slit path-difference measurement", ["effect of wavelength ... on interference patterns"], "high"),
    ("B14b", "Unit 4", "U4AoS1", "Why signal strength is minimum midway between two interference maxima", ["constructive and destructive interference from two sources with reference to ... path difference"], "high"),
    ("B14c", "Unit 4", "U4AoS1", "Explaining what 'polarised' means for an electromagnetic wave", ["explain polarisation of visible light and its relation to a transverse wave model"], "high"),
    ("B15a", "Unit 4", "U4AoS1", "Naming and explaining colour dispersion through a prism", ["investigate and explain theoretically and practically colour dispersion in prisms and lenses"], "high"),
    ("B15b", "Unit 4", "U4AoS1", "Identifying the colours at each end of a dispersed spectrum", ["investigate and explain theoretically and practically colour dispersion in prisms and lenses"], "high"),
    ("B16ai", "Unit 4", "U4AoS2", "Planck's constant from a photoelectric Ek-max-vs-frequency graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B16aii", "Unit 4", "U4AoS2", "Maximum photoelectron-emitting wavelength from the same graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B16aiii", "Unit 4", "U4AoS2", "Work function of the photocell's metal from the same graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B16b", "Unit 4", "U4AoS2", "Sketching a photoelectric graph for a metal with half the work function", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B17a", "Unit 4", "U4AoS2", "Why electrons can produce the same diffraction spacing as X-rays", ["distinguish between the diffraction patterns produced by photons and electrons", "de Broglie wavelength"], "high"),
    ("B17b", "Unit 4", "U4AoS2", "X-ray frequency giving the same diffraction spacing as a given electron beam", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("B18a", "Unit 4", "U4AoS2", "How a hydrogen atom is excited to the n=4 state in one step", ["analyse the absorption of photons by atoms, with reference to: the change in energy levels"], "high"),
    ("B18b", "Unit 4", "U4AoS2", "Possible emitted photon energies for an n=4 to n=2 transition", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B19a", "Unit 4", "U4AoS3", "Plotting force-vs-compression data with uncertainty bars and lines of best fit", ["methods of organising, analysing and evaluating primary data ... sources of uncertainty and error"], "high"),
    ("B19bi", "Unit 3", "U3AoS3", "Spring constant of Spring A from a force-compression graph", ["strain potential energy: ideal springs obeying Hooke's Law"], "high"),
    ("B19bii", "Unit 3", "U3AoS3", "Spring constant of Spring B from the same graph", ["strain potential energy: ideal springs obeying Hooke's Law"], "high"),
    ("B19ci", "Unit 3", "U3AoS3", "Potential energy stored in Spring A at a given compression", ["strain potential energy: area under a force-distance graph"], "high"),
    ("B19cii", "Unit 3", "U3AoS3", "Potential energy stored in the combined spring system", ["strain potential energy: area under a force-distance graph"], "high"),
    ("B19ciii", "Unit 3", "U3AoS3", "Work done compressing Spring B alone", ["work done = area under force-distance graph"], "high"),
    ("B19d", "Unit 3", "U3AoS3", "How a two-spring system suits both small and large suspension bumps", ["strain potential energy: ideal springs obeying Hooke's Law"], "medium"),
]

YEAR = "2019"


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
        "generatedBy": "editorial mapping — each question's own text checked against the official 2017-2023 study design's key knowledge (see scripts/build_2019_curriculum_map.py)",
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
