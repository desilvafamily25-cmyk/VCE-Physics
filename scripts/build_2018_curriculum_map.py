"""Editorial curriculum mapping for the 2018 VCE Physics exam against the
official VCE Physics Study Design 2017-2023 (data/curriculum/study-design-
2016.json). Every mapping below was made by reading each question's actual
text (extracted directly from previous-design-2017-2023/2018-physics-
exam.pdf) against the study design's own key knowledge dot points. This is
deliberately a plain Python literal (not hand-typed JSON) so interactionId
typos fail loudly (KeyError) rather than silently producing an unmapped
question. See scripts/build_2019_curriculum_map.py for the sibling script
this mirrors.

Output: data/curriculum/2018-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2018-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 3", "U3AoS1", "Magnitude of the magnetic force on a current-carrying wire", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("A2", "Unit 3", "U3AoS1", "Direction of the magnetic force on a current-carrying wire", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Identifying the magnetic field pattern around a straight current-carrying wire", ["field shapes and directions, attractive/repulsive effects, dipoles and monopoles"], "high"),
    ("A4", "Unit 3", "U3AoS1", "Electric field strength at a distance from a point charge", ["inverse square law for gravitational and electric fields about a point mass/charge"], "high"),
    ("A5", "Unit 3", "U3AoS3", "Resultant force from four ropes pulling at different angles", ["use vector diagrams to determine the resultant vector of two or more forces"], "high"),
    ("A6", "Unit 3", "U3AoS3", "Braking force on a car from a speed-time graph", ["Newton's three laws of motion: forces along a line"], "high"),
    ("A7", "Unit 3", "U3AoS1", "Gravitational field strength at a distance above Earth's surface", ["gravitational field and gravitational force concepts"], "high"),
    ("A8", "Unit 3", "U3AoS3", "Final speed of two railway trucks after a perfectly inelastic collision", ["conservation of energy and momentum in isolated systems"], "high"),
    ("A9", "Unit 3", "U3AoS3", "Classifying a collision by whether kinetic energy and momentum are conserved", ["conservation of energy and momentum in isolated systems"], "high"),
    ("A10", "Unit 4", "U4AoS1", "Motion of a dust particle from a sound wave passing by it", ["properties of mechanical waves ... investigate and apply theoretically ... transverse and longitudinal waves"], "high"),
    ("A11", "Unit 4", "U4AoS1", "Change heard as a sound source (fire engine) approaches a stationary listener", ["the Doppler effect"], "high"),
    ("A12", "Unit 4", "U4AoS1", "Action that increases dark-band spacing in a double-slit interference pattern", ["effect of wavelength ... on interference patterns"], "high"),
    ("A13", "Unit 3", "U3AoS3", "Graph of the Lorentz factor versus speed for an accelerated electron", ["model mathematically time dilation and length contraction"], "high"),
    ("A14", "Unit 3", "U3AoS3", "Comparing a proton's relativistic and classical kinetic energy", ["comparison of Newton's and Einstein's approach to relativity"], "high"),
    ("A15", "Unit 4", "U4AoS2", "Explaining electron diffraction through Heisenberg's uncertainty principle", ["Heisenberg's Uncertainty Principle as it relates to the position and momentum of a particle"], "high"),
    ("A16", "Unit 4", "U4AoS1", "Identifying polarisation as a property unique to transverse waves", ["explain polarisation of visible light and its relation to a transverse wave model"], "high"),
    ("A17", "Unit 4", "U4AoS2", "Identifying a photoelectric graph for a metal with a larger work function", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("A18", "Unit 4", "U4AoS3", "Defining experimental uncertainty in a measurement", ["precision, accuracy, reliability and validity of data"], "high"),
    ("A19", "Unit 4", "U4AoS3", "Appropriate uncertainty for an analogue ammeter's pointer reading", ["uncertainty as a quantitative estimate ... half the smallest scale division"], "high"),
    ("A20", "Unit 4", "U4AoS3", "Identifying independent, dependent and controlled variables in an induction experiment", ["independent, dependent and controlled variables"], "high"),

    # ---- Section B ----
    ("B1a", "Unit 3", "U3AoS1", "Electric field strength between two accelerating plates", ["potential energy changes in a uniform electric field: W = qV, E = V/d"], "high"),
    ("B1b", "Unit 3", "U3AoS1", "Speed of a proton exiting a uniform electric field", ["potential energy changes in a uniform electric field: W = qV"], "high"),
    ("B1c", "Unit 3", "U3AoS1", "Radius of a proton's circular path in a magnetic field", ["magnetic force on a charged particle: F = qvB", "circular motion"], "high"),
    ("B2a", "Unit 3", "U3AoS2", "Average EMF induced in a loop moving through a magnetic field", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("B2b", "Unit 3", "U3AoS2", "Sketching the induced EMF as a loop passes into, through and out of a field", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("B3a", "Unit 3", "U3AoS2", "Direction of rotation of a model DC motor", ["force on a current-carrying conductor: F = nIlB", "explain the production of DC voltage in DC generators"], "high"),
    ("B3b", "Unit 3", "U3AoS2", "Effect of replacing a DC motor's commutator with slip rings", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("B4a", "Unit 3", "U3AoS2", "Battery voltage giving the same average brightness as an AC alternator", ["household electricity: AC voltage ... RMS voltage and current"], "high"),
    ("B4b", "Unit 3", "U3AoS2", "Sketching a generator's output waveform at double the rotation rate", ["sinusoidal AC voltage: frequency, period, amplitude, peak-to-peak voltage/current"], "high"),
    ("B5a", "Unit 3", "U3AoS2", "Power dissipated in a light globe from its RMS voltage", ["household electricity: ... power in AC circuits"], "high"),
    ("B5b", "Unit 3", "U3AoS2", "Voltage output of a power supply given a transformer ratio and line current", ["ideal transformer action"], "high"),
    ("B5c", "Unit 3", "U3AoS2", "Total power loss in transmission lines from line current and resistance", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B5d", "Unit 3", "U3AoS2", "Power loss in transmission lines with a different transformer ratio", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B5e", "Unit 3", "U3AoS2", "Reasons high voltages are used for long-distance power transmission", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B6a", "Unit 3", "U3AoS3", "Showing a spring constant from energy conservation of a dropped ball", ["strain potential energy: ideal springs obeying Hooke's Law", "conservation of energy"], "high"),
    ("B6b", "Unit 3", "U3AoS3", "Acceleration of a ball at its maximum speed on a spring", ["Newton's three laws of motion: forces along a line"], "high"),
    ("B6c", "Unit 3", "U3AoS3", "Spring compression at the ball's maximum speed", ["strain potential energy: ideal springs obeying Hooke's Law"], "high"),
    ("B7a", "Unit 3", "U3AoS3", "Horizontal distance travelled by a ball rolling off a table", ["motion of projectiles near Earth's surface"], "high"),
    ("B7b", "Unit 3", "U3AoS3", "Height of a table from a ball's projectile fall time", ["motion of projectiles near Earth's surface"], "high"),
    ("B7c", "Unit 3", "U3AoS3", "Speed at which a projectile ball hits the floor", ["motion of projectiles near Earth's surface"], "high"),
    ("B8a", "Unit 3", "U3AoS3", "Force on one pushed block by another (Newton's second law)", ["Newton's three laws of motion: forces along a line"], "high"),
    ("B8b", "Unit 3", "U3AoS3", "Force on the first block by the second (Newton's third law pair)", ["Newton's three laws of motion: ... Newton's third law action/reaction pairs of forces"], "high"),
    ("B9a", "Unit 3", "U3AoS1", "Gravitational force on a spacecraft at a given distance from Jupiter", ["inverse square law for gravitational and electric fields about a point mass/charge"], "high"),
    ("B9b", "Unit 3", "U3AoS1", "Change in gravitational potential energy from a field-distance graph", ["the change in gravitational potential energy from area under a force-distance graph and area under a field-distance graph multiplied by mass"], "high"),
    ("B9c", "Unit 3", "U3AoS1", "Orbital period of a moon from its orbital radius", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B10a", "Unit 3", "U3AoS3", "Radius of an arc giving zero-gravity flight at a given speed", ["Newton's second law to circular motion in a vertical plane"], "high"),
    ("B10b", "Unit 3", "U3AoS3", "Whether gravity is truly zero during a 'zero gravity' flight manoeuvre", ["Newton's second law to circular motion in a vertical plane"], "high"),
    ("B11a", "Unit 4", "U4AoS1", "Wavelength of sound from its speed and frequency", ["wave speed, frequency, wavelength and period: v = f*lambda"], "high"),
    ("B11b", "Unit 4", "U4AoS1", "Distance moved between two quiet (destructive interference) regions", ["constructive and destructive interference from two sources with reference to ... path difference"], "high"),
    ("B12a", "Unit 4", "U4AoS1", "Frequency of laser light before entering an optical fibre", ["wave speed, frequency, wavelength and period: v = f*lambda"], "high"),
    ("B12b", "Unit 4", "U4AoS1", "Critical angle at an optical fibre's cladding-core boundary", ["total internal reflection and critical angle"], "high"),
    ("B12c", "Unit 4", "U4AoS1", "Speed of light inside an optical fibre's core", ["refraction using Snell's Law"], "high"),
    ("B13a", "Unit 4", "U4AoS2", "Number of photons emitted per second from a laser's power output", ["photo energy: E = hf"], "high"),
    ("B13b", "Unit 4", "U4AoS1", "Explaining why the central point of a double-slit pattern is bright", ["constructive and destructive interference from two sources with reference to ... path difference"], "high"),
    ("B13c", "Unit 4", "U4AoS1", "Locating a point in an interference pattern from a given path difference", ["constructive and destructive interference from two sources with reference to ... path difference"], "high"),
    ("B14", "Unit 3", "U3AoS3", "Whether a spaceship at constant velocity is in an inertial frame of reference", ["explain the relationship between force, mass and motion with reference to inertial frames of reference"], "high"),
    ("B15", "Unit 3", "U3AoS3", "Kinetic energy of a spaceship found from its time-dilation factor", ["model mathematically time dilation ... comparison of Newton's and Einstein's approach to relativity"], "high"),
    ("B16", "Unit 3", "U3AoS3", "Time interval observed in a quasar's own frame of reference (time dilation)", ["model mathematically time dilation and length contraction"], "high"),
    ("B17ai", "Unit 4", "U4AoS2", "Identifying the correct claim about a below-threshold-frequency photoelectric experiment", ["threshold frequency required for photoemission to occur for a particular metal"], "high"),
    ("B17aii", "Unit 4", "U4AoS2", "Explaining a misconception that intensity alone can trigger photoemission", ["threshold frequency required for photoemission to occur for a particular metal", "effects of intensity of incident irradiation"], "high"),
    ("B17b", "Unit 4", "U4AoS2", "Planck's constant from a photoelectric Ek-max-vs-frequency graph's gradient", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B17c", "Unit 4", "U4AoS2", "Work function of a metal from a photoelectric graph's intercept", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B18a", "Unit 4", "U4AoS2", "Wavelength of electrons from a diffraction pattern comparison", ["distinguish between the diffraction patterns produced by photons and electrons", "de Broglie wavelength"], "high"),
    ("B18b", "Unit 4", "U4AoS2", "Kinetic energy of electrons from their de Broglie wavelength", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("B19a", "Unit 4", "U4AoS2", "Identifying the visible colour of a hydrogen emission spectral line", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B19b", "Unit 4", "U4AoS2", "Why a hydrogen lamp produces discrete spectral lines", ["explain the production of atomic absorption and emission line spectra", "the change in energy levels"], "high"),
    ("B20a", "Unit 4", "U4AoS3", "Plotting orbital period-squared versus radius-cubed data with a line of best fit", ["methods of organising, analysing and evaluating primary data ... use of appropriate scales, axes and units"], "high"),
    ("B20b", "Unit 4", "U4AoS3", "Gradient of a T-squared versus R-cubed line of best fit", ["methods of organising, analysing and evaluating primary data"], "high"),
    ("B20c", "Unit 3", "U3AoS1", "Mass of Saturn from a T-squared versus R-cubed graph's gradient (Kepler's third law)", ["satellite motion modelled as uniform circular motion"], "high"),
]

YEAR = "2018"


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
        "generatedBy": "editorial mapping — each question's own text checked against the official 2017-2023 study design's key knowledge (see scripts/build_2018_curriculum_map.py)",
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
