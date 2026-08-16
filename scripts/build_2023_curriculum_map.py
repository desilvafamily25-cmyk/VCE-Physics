"""Editorial curriculum mapping for the 2023 VCE Physics exam against the
official VCE Physics Study Design 2017-2023 (data/curriculum/study-design-
2016.json) -- NOT the current 2024-2027 design (see that dataset's own note
for the structural differences: most importantly, relativity content sits in
Unit 3 Area of Study 3 here, not Unit 4). Every mapping below was made by
reading each question's actual text (extracted directly from
previous-design-2017-2023/2023-physics-exam.pdf, dumped to
data/raw/2023-exam-text.txt) against the study design's own key knowledge
dot points. This is deliberately a plain Python literal (not hand-typed
JSON) so interactionId typos fail loudly (KeyError) rather than silently
producing an unmapped question. See scripts/build_2025_curriculum_map.py for
the sibling script this mirrors.

Output: data/curriculum/2023-mapping.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "curriculum" / "2023-mapping.json"

# (interactionId, unit, areaOfStudy, topic, skills, confidence)
MAPPING = [
    # ---- Section A ----
    ("A1", "Unit 3", "U3AoS1", "Magnetic polarity from the force on a current-carrying coil", ["force on a current-carrying conductor: F = nIlB"], "high"),
    ("A2", "Unit 3", "U3AoS1", "Coulomb force when charge and separation are both halved", ["inverse square law for gravitational and electric fields about a point mass/charge"], "high"),
    ("A3", "Unit 3", "U3AoS1", "Satellite altitude where gravitational field strength is halved", ["inverse square law for gravitational fields", "satellite motion modelled as uniform circular motion"], "high"),
    ("A4", "Unit 3", "U3AoS3", "Impulse from a force-time graph (tennis racquet impact)", ["impulse in an isolated system: F*delta t = m*delta v"], "high"),
    ("A5", "Unit 3", "U3AoS2", "Globe brightness before/during/after a magnetic field is switched off", ["generation of emf", "rate of change of magnetic flux"], "high"),
    ("A6", "Unit 3", "U3AoS2", "Magnetic flux magnitude through a coil", ["magnetic flux: Phi = B*A"], "high"),
    ("A7", "Unit 3", "U3AoS2", "Peak-to-peak voltage and frequency from an oscilloscope trace", ["sinusoidal AC voltage: frequency, period, amplitude, peak-to-peak voltage/current"], "high"),
    ("A8", "Unit 3", "U3AoS3", "Why two falling people of different mass reach the water together", ["Newton's three laws of motion", "projectile motion near Earth's surface"], "high"),
    ("A9", "Unit 3", "U3AoS3", "Banked-track angle for a velodrome with no sideways friction", ["uniform circular motion (vehicle on a banked track)"], "high"),
    ("A10", "Unit 3", "U3AoS3", "Spring constant from a force-compression graph", ["strain potential energy: ideal springs obeying Hooke's Law"], "high"),
    ("A11", "Unit 3", "U3AoS3", "Additional strain potential energy stored under further compression", ["strain potential energy: area under a force-distance graph"], "high"),
    ("A12", "Unit 4", "U4AoS1", "Colour dispersion of white light through a lens", ["colour dispersion in prisms and lenses"], "high"),
    ("A13", "Unit 4", "U4AoS1", "Classifying sound and light as longitudinal or transverse waves", ["distinguish between transverse and longitudinal waves"], "high"),
    ("A14", "Unit 4", "U4AoS1", "Polarisation as evidence for the transverse wave model of light", ["polarisation of visible light and its relation to the transverse wave model"], "high"),
    ("A15", "Unit 4", "U4AoS1", "Doppler effect for two ambulances moving towards/away from an observer", ["qualitative explanation of the Doppler effect"], "high"),
    ("A16", "Unit 4", "U4AoS1", "Identifying refraction as water waves change direction at a barrier", ["refraction: Snell's Law"], "high"),
    ("A17", "Unit 4", "U4AoS2", "Why X-ray and electron diffraction patterns can be compared", ["electron diffraction patterns as evidence for the wave-like nature of matter", "distinguishing diffraction patterns produced by photons and electrons"], "high"),
    ("A18", "Unit 4", "U4AoS2", "Coherence and wavelength range of different light sources", ["production of light in lasers, synchrotrons, LEDs and incandescent lights"], "high"),
    ("A19", "Unit 4", "U4AoS2", "Frequency of a spectral line from a hydrogen emission spectrum", ["atomic absorption and emission line spectra", "photon energy from spectral transitions: delta E = hf"], "high"),
    ("A20", "Unit 4", "U4AoS2", "Heisenberg's uncertainty principle in single-slit electron diffraction", ["Heisenberg's uncertainty principle illustrated via single-slit diffraction"], "high"),

    # ---- Section B ----
    ("B1a", "Unit 3", "U3AoS1", "Force diagram for charged balls in electrostatic/gravitational equilibrium", ["field model for gravitation, magnetism and electricity"], "high"),
    ("B1b", "Unit 3", "U3AoS1", "Tension force from a suspended charged-ball equilibrium", ["Newton's three laws of motion: coplanar forces"], "high"),
    ("B1c", "Unit 3", "U3AoS1", "Electrostatic force between two suspended charged balls", ["inverse square law for electric fields about a point charge"], "high"),
    ("B2a", "Unit 3", "U3AoS1", "Gravitational field strength above a planet's surface", ["inverse square law for gravitational fields"], "high"),
    ("B2b", "Unit 3", "U3AoS1", "Orbital period of a moon in circular orbit", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B2c", "Unit 3", "U3AoS1", "Effect of a shrinking orbital radius on orbital period", ["satellite motion modelled as uniform circular motion"], "high"),
    ("B3a", "Unit 3", "U3AoS1", "Sketching the magnetic field around two parallel current-carrying wires", ["magnetic fields of ... current-carrying wires, loops and solenoids"], "high"),
    ("B3b", "Unit 3", "U3AoS1", "Whether two antiparallel current-carrying wires attract or repel", ["describe the interaction of two fields ... current carrying conductors can either attract or repel"], "high"),
    ("B4a", "Unit 3", "U3AoS2", "Primary-to-secondary turns ratio of an ideal transformer", ["ideal transformer action"], "high"),
    ("B4b", "Unit 3", "U3AoS2", "Primary coil current of a transformer supplying a known load", ["ideal transformer action"], "high"),
    ("B4c", "Unit 3", "U3AoS2", "Why a transformer needs AC rather than constant DC input", ["ideal transformer action", "generation of emf"], "high"),
    ("B5a", "Unit 3", "U3AoS2", "Average EMF induced as a loop enters a magnetic field", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("B5b", "Unit 3", "U3AoS2", "Direction of induced current as a loop enters a magnetic field", ["direction of induced emf in a coil"], "high"),
    ("B6a", "Unit 3", "U3AoS2", "Why a particular magnet arrangement fails to generate an EMF", ["generation of emf ... rate of change of magnetic flux"], "high"),
    ("B6b", "Unit 3", "U3AoS2", "Repositioning magnets so a simple generator produces an EMF", ["explain the production of DC voltage in DC generators ... split ring commutators"], "high"),
    ("B7a", "Unit 3", "U3AoS2", "Total resistance of a transmission line from power-loss data", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B7b", "Unit 3", "U3AoS2", "Voltage available at the far end of a transmission line", ["analyse the supply of power by considering transmission losses"], "high"),
    ("B7c", "Unit 3", "U3AoS2", "Effect of transmitting at a much lower voltage on line losses", ["identify the advantage of the use of AC power", "transmission losses"], "high"),
    ("B8a", "Unit 3", "U3AoS3", "Force diagram for a skateboarder rolling down a slope", ["Newton's three laws of motion: coplanar forces along a straight line and in two dimensions"], "high"),
    ("B8b", "Unit 3", "U3AoS3", "Total frictional force on a skateboarder at constant velocity", ["Newton's three laws of motion"], "high"),
    ("B8c", "Unit 3", "U3AoS3", "What happens to momentum and kinetic energy when coming to rest", ["conservation of energy and momentum in isolated systems", "energy dissipated to the environment"], "high"),
    ("B9a", "Unit 3", "U3AoS3", "Time of flight for a ball thrown vertically and caught at the same height", ["motion of projectiles near Earth's surface"], "high"),
    ("B9b", "Unit 3", "U3AoS3", "Speed of a racquet head modelled as uniform circular motion", ["uniform circular motion of an object moving in a horizontal plane"], "high"),
    ("B9c", "Unit 3", "U3AoS3", "Height of a served ball above a net (2D projectile motion)", ["motion of projectiles near Earth's surface"], "high"),
    ("B10a", "Unit 3", "U3AoS3", "Proton speed from its Lorentz factor", ["model mathematically time dilation and length contraction"], "high"),
    ("B10b", "Unit 3", "U3AoS3", "Beamline length in the proton's own reference frame (length contraction)", ["proper length (L0)", "length contraction: L = L0/gamma"], "high"),
    ("B10c", "Unit 3", "U3AoS3", "Relativistic kinetic energy of an accelerated proton", ["mass-energy equivalence: Ek = (gamma - 1)mc^2"], "high"),
    ("B11a", "Unit 4", "U4AoS1", "Frequency of a standing wave on a guitar string", ["wave speed, frequency, wavelength and period: v = f*lambda"], "high"),
    ("B11b", "Unit 4", "U4AoS1", "How a standing wave forms on a string fixed at both ends", ["standing waves in strings fixed at one or both ends"], "high"),
    ("B12a", "Unit 4", "U4AoS1", "Critical angle for total internal reflection in a glass prism", ["total internal reflection and critical angle"], "high"),
    ("B12b", "Unit 4", "U4AoS1", "Whether total internal reflection occurs at a prism face", ["total internal reflection and critical angle"], "high"),
    ("B13a", "Unit 4", "U4AoS1", "Path difference between two rays in a double-slit interference pattern", ["Young's double slit experiment: path differences"], "high"),
    ("B13b", "Unit 4", "U4AoS1", "Effect of switching to a longer wavelength laser on fringe spacing", ["effect of wavelength ... on interference patterns"], "high"),
    ("B13c", "Unit 4", "U4AoS1", "Young's double-slit experiment as evidence for the wave-like nature of light", ["explain the results of Young's double slit experiment: evidence for the wave-like nature of light"], "high"),
    ("B14a", "Unit 4", "U4AoS2", "Neutron speed from a given de Broglie wavelength", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("B14b", "Unit 4", "U4AoS2", "Whether a neutron beam will diffract through a crystal lattice", ["effects of varying the width of a gap or diameter of an obstacle on the diffraction pattern"], "high"),
    ("B14c", "Unit 4", "U4AoS2", "Comparing electron and neutron speed at equal de Broglie wavelength", ["calculate the de Broglie wavelength of matter: lambda = h/p"], "high"),
    ("B15a", "Unit 4", "U4AoS2", "Work function of calcium estimated from a photoelectric-effect graph", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B15b", "Unit 4", "U4AoS2", "Maximum photoelectron-emitting wavelength for calcium", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B15c", "Unit 4", "U4AoS2", "Sketching the photoelectric graph for a metal with a different work function", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B15d", "Unit 4", "U4AoS2", "Whether photoelectrons are ejected by a given photon wavelength", ["kinetic energy of emitted photoelectrons: Ek max = hf - phi"], "high"),
    ("B16a", "Unit 4", "U4AoS2", "Photon energy of a mercury emission spectral line", ["interpret spectra and calculate the energy of absorbed or emitted photons: delta E = hf"], "high"),
    ("B16b", "Unit 4", "U4AoS2", "Marking a transition arrow on a mercury energy-level diagram", ["explain the production of atomic absorption and emission line spectra"], "high"),
    ("B16c", "Unit 4", "U4AoS2", "Possible re-emitted photon energies after absorption to an excited state", ["analyse the absorption of photons by atoms: change in energy levels"], "high"),
    ("B17a", "Unit 3", "U3AoS1", "Electron speed after acceleration through a potential difference", ["electric field acceleration of a charge: F = qE, W = qV"], "high"),
    ("B17b", "Unit 3", "U3AoS1", "Why a charged particle follows a circular arc in a magnetic field", ["magnetic force on a charged particle: F = qvB"], "high"),
    ("B17c", "Unit 3", "U3AoS1", "Relating mass, charge, speed, field and radius for circular motion in a field", ["radius of the path followed by a low-velocity electron in a magnetic field"], "medium"),
    ("B17d", "Unit 4", "U4AoS3", "Identifying independent, dependent and controlled variables in an e/m experiment", ["independent, dependent and controlled variables"], "high"),
    ("B17e", "Unit 4", "U4AoS3", "Completing a data table of measured values", ["methods of organising ... primary data"], "high"),
    ("B17f", "Unit 4", "U4AoS3", "Plotting experimental data with uncertainty bars and a line of best fit", ["methods of organising, analysing and evaluating primary data ... sources of uncertainty and error"], "high"),
    ("B17g", "Unit 4", "U4AoS3", "Gradient of a linearised V0-vs-r^2 graph", ["methods of organising, analysing and evaluating primary data"], "medium"),
    ("B17h", "Unit 3", "U3AoS1", "Deriving the charge-to-mass ratio e/m from a graph's gradient", ["radius of the path followed by a low-velocity electron in a magnetic field"], "medium"),
]

YEAR = "2023"


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
        "generatedBy": "editorial mapping — each question's own text (data/raw/2023-exam-text.txt) checked against the official 2017-2023 study design's key knowledge (see scripts/build_2023_curriculum_map.py)",
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
