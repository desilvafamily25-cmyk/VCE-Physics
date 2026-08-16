"""Editorial curriculum mapping for the 2022 VCE Physics exam against the
official VCE Physics Study Design 2017-2023 (data/curriculum/study-design-
2016.json). Every mapping below was made by reading each question's actual
text (extracted directly from previous-design-2017-2023/2022-physics-
exam.pdf, dumped to data/raw/2022-exam-text.txt) against the study design's
own key knowledge dot points. This is deliberately a plain Python literal
(not hand-typed JSON) so interactionId typos fail loudly (KeyError) rather
than silently producing an unmapped question. See
scripts/build_2023_curriculum_map.py for the sibling script this mirrors.

Output: data/curriculum/2022-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2022-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 3", "U3AoS1", "Magnetic field direction at the centre of a current-carrying loop", ["magnetic fields of ... current-carrying wires, loops and solenoids"], "high"),
    ("A2", "Unit 3", "U3AoS2", "Frequency of a generator's magnetic-flux-vs-time graph", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Charge sign of particles from their deflection in a magnetic field", ["magnetic force on a charged particle: F = qvB"], "high"),
    ("A4", "Unit 3", "U3AoS1", "Point of zero electric field between two unequal point charges", ["inverse square law for gravitational and electric fields about a point mass/charge"], "high"),
    ("A5", "Unit 3", "U3AoS2", "Generator output-voltage trace when rotation frequency doubles", ["sinusoidal AC voltage: frequency, period, amplitude, peak-to-peak voltage/current"], "high"),
    ("A6", "Unit 3", "U3AoS3", "Mass of a second railway truck from momentum conservation", ["conservation of energy and momentum in isolated systems"], "high"),
    ("A7", "Unit 3", "U3AoS3", "Newton's third law forces during a collision", ["Newton's three laws of motion"], "high"),
    ("A8", "Unit 3", "U3AoS3", "Spring compression for a given stored strain potential energy", ["strain potential energy: ideal springs obeying Hooke's Law"], "high"),
    ("A9", "Unit 3", "U3AoS3", "Tension force on each end of a rope pulled by two people", ["Newton's three laws of motion: coplanar forces along a straight line"], "high"),
    ("A10", "Unit 4", "U4AoS1", "Correct description of the Doppler effect for sound", ["qualitative explanation of the Doppler effect"], "high"),
    ("A11", "Unit 4", "U4AoS1", "Distinguishing transverse and longitudinal wave vibration direction", ["distinguish between transverse and longitudinal waves"], "high"),
    ("A12", "Unit 4", "U4AoS1", "Minimum refractive index for total internal reflection in a submerged prism", ["total internal reflection and critical angle"], "high"),
    ("A13", "Unit 4", "U4AoS1", "Wave speed from a standing wave's node spacing and period", ["wave speed, frequency, wavelength and period", "standing waves in strings fixed at one or both ends"], "high"),
    ("A14", "Unit 4", "U4AoS2", "Best evidence that electrons behave as waves", ["electron diffraction patterns as evidence for the wave-like nature of matter"], "high"),
    ("A15", "Unit 4", "U4AoS2", "Best evidence that light behaves as a particle", ["the photoelectric effect as evidence for the particle-like nature of light"], "high"),
    ("A16", "Unit 4", "U4AoS1", "Phenomenon that best demonstrates light waves are transverse", ["polarisation of visible light and its relation to the transverse wave model"], "high"),
    ("A17", "Unit 4", "U4AoS2", "Frequency of a gamma photon from its energy", ["interpret spectra and calculate the energy of absorbed or emitted photons: delta E = hf"], "high"),
    ("A18", "Unit 3", "U3AoS3", "Identifying an inertial frame of reference", ["Einstein's postulates of special relativity: inertial (non-accelerated) frames"], "high"),
    ("A19", "Unit 3", "U3AoS3", "Lorentz factor for a particle close to the speed of light", ["model mathematically time dilation and length contraction"], "high"),
    ("A20", "Unit 4", "U4AoS3", "Definition of experimental uncertainty", ["error and uncertainty"], "high"),

    # ---- Section B ----
    ("B1a", "Unit 3", "U3AoS2", "Current direction in a DC motor coil at a given position", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("B1b", "Unit 3", "U3AoS2", "Current direction in a DC motor coil at a different position", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("B1c", "Unit 3", "U3AoS2", "Current magnitude from a magnetic force on a motor coil side", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("B2a", "Unit 3", "U3AoS1", "Why geostationary satellites must orbit above the equator", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B2b", "Unit 3", "U3AoS1", "Altitude of a geostationary satellite from orbital period", ["satellite motion modelled as uniform circular motion", "inverse square law for gravitational fields"], "high"),
    ("B2c", "Unit 3", "U3AoS1", "Orbital speed of a geostationary satellite", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B3a", "Unit 3", "U3AoS1", "Kinetic energy gained by an ion accelerated through a potential difference", ["electric field acceleration of a charge: F = qE, W = qV"], "high"),
    ("B3b", "Unit 3", "U3AoS1", "Ion speed after acceleration through a potential difference", ["electric field acceleration of a charge: F = qE, W = qV"], "high"),
    ("B3c", "Unit 3", "U3AoS1", "Diameter of a charged particle's semicircular path in a magnetic field", ["radius of the path followed by a low-velocity electron in a magnetic field"], "high"),
    ("B4", "Unit 3", "U3AoS2", "Induced EMF and current for three different loop-vs-wire movements", ["investigate and analyse ... the generation of electromotive force (emf)", "rate of change of magnetic flux"], "high"),
    ("B5a", "Unit 3", "U3AoS2", "Power produced by a wind generator from RMS voltage and current", ["compare sinusoidal AC voltages ... root-mean-square (rms)"], "high"),
    ("B5b", "Unit 3", "U3AoS2", "Whether transmission-line losses leave enough power for a factory", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B5c", "Unit 3", "U3AoS2", "Power delivered after installing step-up/step-down transformers", ["ideal transformer action", "transmission losses"], "high"),
    ("B6a", "Unit 3", "U3AoS2", "Magnetic field strength from a known magnetic flux", ["magnetic flux: Phi = B*A"], "high"),
    ("B6b", "Unit 3", "U3AoS2", "Average induced EMF over a quarter rotation of a coil", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("B7ai", "Unit 3", "U3AoS3", "Component of gravitational force down an inclined ramp", ["Newton's three laws of motion: coplanar forces in two dimensions"], "high"),
    ("B7aii", "Unit 3", "U3AoS3", "Constant frictional force opposing motion down a ramp", ["Newton's three laws of motion"], "high"),
    ("B7bi", "Unit 3", "U3AoS3", "Speed of two trolleys after a perfectly inelastic collision", ["conservation of energy and momentum in isolated systems"], "high"),
    ("B7bii", "Unit 3", "U3AoS3", "Determining whether a trolley collision is elastic or inelastic", ["elastic and inelastic collisions with reference to conservation of kinetic energy"], "high"),
    ("B8a", "Unit 3", "U3AoS3", "Net force on a car cornering at constant speed", ["uniform circular motion of an object moving in a horizontal plane: a vehicle moving around a circular road"], "high"),
    ("B8b", "Unit 3", "U3AoS3", "Direction of the net centripetal force on a cornering car", ["uniform circular motion of an object moving in a horizontal plane"], "high"),
    ("B8c", "Unit 3", "U3AoS3", "Why a car needs a net horizontal force to corner, and what supplies it", ["uniform circular motion of an object moving in a horizontal plane"], "high"),
    ("B9", "Unit 3", "U3AoS3", "Energy transformation in a star and its effect on stellar mass", ["interpret Einstein's prediction ... mass-energy equivalence", "nuclear fusion in the Sun"], "high"),
    ("B10a", "Unit 4", "U4AoS3", "Classifying variables in a projectile-motion investigation", ["independent, dependent and controlled variables"], "high"),
    ("B10b", "Unit 4", "U4AoS3", "Plotting range-vs-angle data with uncertainty bars and a curve of best fit", ["methods of organising, analysing and evaluating primary data ... sources of uncertainty and error"], "high"),
    ("B10c", "Unit 4", "U4AoS3", "Reading maximum range and its angle off an experimental graph", ["methods of organising, analysing and evaluating primary data"], "high"),
    ("B10di", "Unit 3", "U3AoS3", "Theoretical projectile range from the range formula", ["motion of projectiles near Earth's surface"], "high"),
    ("B10dii", "Unit 3", "U3AoS3", "Evaluating whether air resistance can be ignored against experimental data", ["qualitative description of the effects of air resistance"], "medium"),
    ("B11", "Unit 3", "U3AoS3", "Why muons reach Earth's surface despite their short half-life", ["explain why muons can reach Earth even though their half-lives would suggest that they should decay in the outer atmosphere"], "high"),
    ("B12a", "Unit 4", "U4AoS1", "Why the central band is bright and an adjacent band is dark", ["constructive and destructive interference from two sources ... path difference"], "high"),
    ("B12b", "Unit 4", "U4AoS1", "How Young's double-slit experiment supports the wave model of light", ["explain the results of Young's double slit experiment: evidence for the wave-like nature of light"], "high"),
    ("B12c", "Unit 4", "U4AoS1", "Spacing of dark interference bands from wavelength and geometry", ["effect of wavelength, distance of screen and slit separation on interference patterns"], "high"),
    ("B12d", "Unit 4", "U4AoS1", "Effect of immersing a double-slit apparatus in a liquid on fringe spacing", ["investigate and analyse theoretically and practically the behaviour of waves including refraction"], "medium"),
    ("B13a", "Unit 4", "U4AoS1", "Horizontal distance travelled by a refracted ray to the tank floor", ["refraction using Snell's Law"], "high"),
    ("B13b", "Unit 4", "U4AoS1", "Colour dispersion and total internal reflection of white light entering water", ["investigate and explain theoretically and practically colour dispersion in prisms and lenses"], "high"),
    ("B14a", "Unit 4", "U4AoS2", "Identifying the stopping-voltage point on a photoelectric current-voltage graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B14b", "Unit 4", "U4AoS2", "Effect of increased light intensity on a photoelectric current-voltage graph", ["effects of intensity of incident irradiation on the emission of photoelectrons"], "high"),
    ("B14c", "Unit 4", "U4AoS2", "Effect of a higher-frequency filter on a photoelectric current-voltage graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B14d", "Unit 4", "U4AoS2", "Work function of a metal from a Ek-max-vs-frequency graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B14e", "Unit 4", "U4AoS2", "Planck's constant from the gradient of a Ek-max-vs-frequency graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B14f", "Unit 4", "U4AoS2", "A limitation of the wave model in explaining the photoelectric effect", ["describe the limitation of the wave model of light in explaining experimental results related to the photoelectric effect"], "high"),
    ("B15a", "Unit 4", "U4AoS2", "Photon energy transition for a given emitted wavelength", ["interpret spectra and calculate the energy of absorbed or emitted photons: delta E = hf"], "high"),
    ("B15b", "Unit 4", "U4AoS2", "Marking the correct transition arrow on an energy-level diagram", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B16a", "Unit 4", "U4AoS1", "Condition on gap size for a diffraction pattern to form", ["effect of changing gap width or obstacle size on a diffraction pattern"], "high"),
    ("B16b", "Unit 4", "U4AoS1", "Why an open window produces no observable diffraction pattern", ["effect of changing gap width or obstacle size on a diffraction pattern"], "high"),
    ("B17a", "Unit 4", "U4AoS2", "De Broglie wavelength of electrons from their kinetic energy", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("B17b", "Unit 4", "U4AoS2", "Effect of a small speed increase on the de Broglie wavelength", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
]

YEAR = "2022"


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
        "generatedBy": "editorial mapping — each question's own text (data/raw/2022-exam-text.txt) checked against the official 2017-2023 study design's key knowledge (see scripts/build_2022_curriculum_map.py)",
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
