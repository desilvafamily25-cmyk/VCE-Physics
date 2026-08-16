"""Editorial curriculum mapping for the 2017 VCE Physics exam against the
official VCE Physics Study Design 2017-2023 (data/curriculum/study-design-
2016.json). Every mapping below was made by reading each question's actual
text (extracted directly from previous-design-2017-2023/2017-physics-
exam.pdf) against the study design's own key knowledge dot points. This is
deliberately a plain Python literal (not hand-typed JSON) so interactionId
typos fail loudly (KeyError) rather than silently producing an unmapped
question. See scripts/build_2018_curriculum_map.py for the sibling script
this mirrors. 2017 is the first year of this study design's examination.

Output: data/curriculum/2017-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2017-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 3", "U3AoS1", "Identifying that a magnetic monopole cannot currently be created", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles"], "high"),
    ("A2", "Unit 3", "U3AoS1", "Electric force on a charged oil drop in a uniform field (Millikan)", ["force on a charge in a uniform electric field: F = qE"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Voltage between charged plates from electric field strength and separation", ["potential energy changes in a uniform electric field: W = qV, E = V/d"], "high"),
    ("A4", "Unit 3", "U3AoS2", "Turns ratio of a step-down transformer", ["ideal transformer action"], "high"),
    ("A5", "Unit 3", "U3AoS2", "Peak current in a transformer's secondary coil from its RMS power", ["ideal transformer action", "peak and RMS values of AC voltage and current"], "high"),
    ("A6", "Unit 3", "U3AoS2", "Induced EMF graph from a magnetic-flux-versus-time graph", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("A7", "Unit 3", "U3AoS3", "Acceleration of a model car from a constant applied force", ["Newton's three laws of motion: forces along a line"], "high"),
    ("A8", "Unit 3", "U3AoS3", "Impulse given to a car by a constant force over a time interval", ["impulse in a system: F*t = m*deltav"], "high"),
    ("A9", "Unit 3", "U3AoS3", "Final speed of a car after constant acceleration from rest", ["Newton's three laws of motion: forces along a line"], "high"),
    ("A10", "Unit 3", "U3AoS3", "Comparing experiment results in accelerating versus inertial frames of reference", ["explain the relationship between force, mass and motion with reference to inertial frames of reference"], "high"),
    ("A11", "Unit 3", "U3AoS3", "Mass lost by the Sun each second from its radiated energy", ["mass-energy equivalence: E = mc^2"], "high"),
    ("A12", "Unit 3", "U3AoS3", "Spring constant estimated from a force-distance graph", ["strain potential energy: ideal springs obeying Hooke's Law"], "high"),
    ("A13", "Unit 3", "U3AoS3", "Initial kinetic energy of a car from the area under a force-distance graph", ["work done = area under force-distance graph", "conservation of energy"], "high"),
    ("A14", "Unit 4", "U4AoS1", "Explaining why sound diffracts noticeably around a doorway", ["the extent of diffraction ... is affected by the ratio of wavelength to obstacle/aperture width"], "high"),
    ("A15", "Unit 4", "U4AoS1", "Frequency change heard as a siren approaches then recedes (Doppler effect)", ["the Doppler effect"], "high"),
    ("A16", "Unit 4", "U4AoS2", "Explaining electron diffraction through Heisenberg's uncertainty principle", ["Heisenberg's Uncertainty Principle as it relates to the position and momentum of a particle"], "high"),
    ("A17", "Unit 4", "U4AoS2", "Explaining quantised atomic energy levels via electron standing waves", ["explain the production of atomic absorption and emission line spectra", "de Broglie wavelength"], "high"),
    ("A18", "Unit 4", "U4AoS3", "Comparing the accuracy and precision of two students' repeated measurements", ["precision, accuracy, reliability and validity of data"], "high"),
    ("A19", "Unit 4", "U4AoS3", "Identifying the best description of a scientific hypothesis", ["the characteristics of scientific methodology"], "high"),
    ("A20", "Unit 4", "U4AoS3", "Distinguishing how repeated readings affect systematic versus random errors", ["identify and distinguish between random and systematic errors"], "high"),

    # ---- Section B ----
    ("B1", "Unit 3", "U3AoS1", "Direction of the resultant electric field at a point between three charges", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles", "inverse square law"], "high"),
    ("B2a", "Unit 3", "U3AoS1", "Showing the Coulomb force between a proton and an electron in a hydrogen atom", ["inverse square law for gravitational and electric fields about a point mass/charge: F = kq1q2/r^2"], "high"),
    ("B2b", "Unit 3", "U3AoS1", "Speed of an electron in a circular orbit from the Coulomb force", ["magnetic force on a charged particle", "circular motion modelled with Newton's second law"], "high"),
    ("B3a", "Unit 3", "U3AoS2", "Size and direction of the magnetic force on a DC motor coil's side", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B3b", "Unit 3", "U3AoS2", "Force on a motor coil's other side in the same orientation", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B4a", "Unit 3", "U3AoS1", "Gravitational field strength at the surface of Pluto", ["gravitational field and gravitational force concepts"], "high"),
    ("B4b", "Unit 3", "U3AoS1", "Orbital period of Pluto's moon Charon", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B4c", "Unit 3", "U3AoS1", "Evaluating claims about orbital speed depending on a satellite's own mass", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B5a", "Unit 3", "U3AoS2", "Magnitude of the magnetic field from an alternator's flux and coil geometry", ["magnetic flux: Phi = B*A"], "high"),
    ("B5b", "Unit 3", "U3AoS2", "Average EMF generated by an alternator in a quarter turn", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("B5c", "Unit 3", "U3AoS2", "Sketching an alternator's output after replacing slip rings with a commutator", ["explain the production of DC voltage in DC generators"], "high"),
    ("B6a", "Unit 3", "U3AoS2", "Total power loss in transmission lines from line current and resistance", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B6b", "Unit 3", "U3AoS2", "Factor increase in transmission power loss from a lower transformer ratio", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B7a", "Unit 3", "U3AoS3", "Drawing the forces on a rider and bicycle on a banked circular track", ["Newton's second law to circular motion in a vertical plane", "use vector diagrams to determine the resultant vector of two or more forces"], "high"),
    ("B7b", "Unit 3", "U3AoS3", "Angle of bank giving no sideways friction force on a circular track", ["Newton's second law to circular motion in a vertical plane"], "high"),
    ("B8a", "Unit 3", "U3AoS3", "Speed giving zero normal reaction force at the top of a circular arc", ["Newton's second law to circular motion in a vertical plane"], "high"),
    ("B8b", "Unit 3", "U3AoS3", "Speed at the bottom of an arc from energy conservation", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B9a", "Unit 3", "U3AoS3", "Height of a projectile ball above the ground when it strikes a wall", ["motion of projectiles near Earth's surface"], "high"),
    ("B9b", "Unit 4", "U4AoS3", "Identifying controlled, dependent and independent variables in a projectile investigation", ["independent, dependent and controlled variables"], "high"),
    ("B9c", "Unit 4", "U4AoS3", "Plotting projectile-range data with uncertainty bars and a curve of best fit", ["methods of organising, analysing and evaluating primary data ... sources of uncertainty and error"], "high"),
    ("B10", "Unit 3", "U3AoS3", "Speed of a spaceship from a measured length-contraction ratio", ["model mathematically time dilation and length contraction"], "high"),
    ("B11a", "Unit 3", "U3AoS3", "Lifetime of a decaying particle in the laboratory's frame of reference", ["model mathematically time dilation and length contraction"], "high"),
    ("B11b", "Unit 3", "U3AoS3", "Distance travelled by a particle as measured in its own frame of reference", ["model mathematically time dilation and length contraction"], "high"),
    ("B11c", "Unit 3", "U3AoS3", "Why more particles are observed than classical physics would predict", ["model mathematically time dilation and length contraction", "comparison of Newton's and Einstein's approach to relativity"], "high"),
    ("B12", "Unit 3", "U3AoS3", "Determining whether a trolley collision is elastic or inelastic", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B13a", "Unit 3", "U3AoS3", "Distance a spring stretches before a falling mass momentarily stops", ["strain potential energy: ideal springs obeying Hooke's Law", "conservation of energy"], "high"),
    ("B13b", "Unit 3", "U3AoS3", "How kinetic, gravitational and strain energy vary as a mass falls onto a spring", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B14a", "Unit 4", "U4AoS1", "Critical angle for total internal reflection from glucose solution to air", ["total internal reflection and critical angle"], "high"),
    ("B14b", "Unit 4", "U4AoS1", "Sketching the refracted ray below the critical angle", ["refraction using Snell's Law"], "high"),
    ("B14c", "Unit 4", "U4AoS1", "Explaining why an observer beyond the critical angle cannot see the laser", ["total internal reflection and critical angle"], "high"),
    ("B15a", "Unit 4", "U4AoS1", "Wavelength of a 680 Hz sound from its speed", ["wave speed, frequency, wavelength and period: v = f*lambda"], "high"),
    ("B15b", "Unit 4", "U4AoS1", "Evaluating predictions about combined-loudspeaker sound intensity", ["constructive and destructive interference from two sources with reference to ... path difference"], "high"),
    ("B15c", "Unit 4", "U4AoS1", "Comparing sound intensity heard by two students from path difference", ["constructive and destructive interference from two sources with reference to ... path difference"], "high"),
    ("B16a", "Unit 4", "U4AoS1", "Wavelength of the lowest-frequency standing wave on a fixed string", ["standing waves in strings fixed at one or both ends"], "high"),
    ("B16b", "Unit 4", "U4AoS1", "Frequency of the second-lowest resonance on a fixed string", ["standing waves in strings fixed at one or both ends"], "high"),
    ("B16c", "Unit 4", "U4AoS1", "Explaining with a diagram how standing waves form on a string", ["standing waves in strings fixed at one or both ends"], "high"),
    ("B17a", "Unit 4", "U4AoS2", "Cut-off (stopping) potential for a given light frequency on a photocell", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B17b", "Unit 4", "U4AoS2", "Sketching a photoelectric current graph for higher-intensity UV light", ["effects of intensity of incident irradiation on the emission of photoelectrons"], "high"),
    ("B17c", "Unit 4", "U4AoS2", "Aspects of the photoelectric effect that evidence light's particle nature", ["compare wave and particle models used to explain the photoelectric effect"], "high"),
    ("B18a", "Unit 4", "U4AoS2", "Drawing an atomic transition producing a 1.65 eV emitted photon", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B18b", "Unit 4", "U4AoS2", "Shortest possible photon wavelength for a decay from n=5 to ground state", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B18c", "Unit 4", "U4AoS2", "Explaining why an impossible spectral line energy cannot be observed", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B19", "Unit 4", "U4AoS2", "Evaluating claims about electron diffraction and describing supporting experiments", ["distinguish between the diffraction patterns produced by photons and electrons", "de Broglie wavelength"], "high"),
]

YEAR = "2017"


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
        "generatedBy": "editorial mapping — each question's own text checked against the official 2017-2023 study design's key knowledge (see scripts/build_2017_curriculum_map.py)",
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
