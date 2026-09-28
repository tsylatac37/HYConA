# SIH 2026 — Problem Statement Selection Report

**Prepared for:** Team decision-making (6-member undergraduate team, sophomore-level)
**Scope:** All six Hardware-category problem statements reviewed — evaluated for difficulty, doability, and feasibility from a sophomore team's perspective.

---

## 1. Quick Reference — Ranking Summary

| Rank | PS ID | Title (short) | Organization | Difficulty | Doability | Feasibility | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | **26025** | Mine Subsidence Monitoring | Ministry of Coal | Low–Medium | High | High | **Best pick** |
| 2 | **26172** | Voice Activator (KWS) | ISRO | Medium | High | High | **Strong second** |
| 3 | **26049** | HAA/SHAA Electronics Reliability | DRDO | Medium–High | Medium–High (if scoped) | Medium–High | **Solid third choice** |
| 4 | **26185** | Conformal Helmet Antenna | Ministry of Home Affairs (NSG) | Medium–High | Medium (gated by RF lab access) | Medium | **Conditional — only with EM/RF lab access** |
| 5 | **26026** | Quadruped/Handheld Narcotics & Explosives Detection | Ministry of Railways | Very High | Low | Low | **Red flag — avoid** |
| 6 | **26050** | Anti-Drone High-Altitude Hardening | DRDO | Very High+ | Low | Very Low | **Red flag — avoid** |

**Recommended preference order:** 26025 → 26172 → 26049 → (26185 conditionally) → do not list 26026/26050 unless no other option remains.

---

## 2. Detailed Breakdown

### PS 26025 — Mine Subsidence Monitoring, Prediction & Early Warning
**Organization:** Ministry of Coal | **Theme:** Disaster Management | **Target HW:** LoRa/Zigbee mesh sensor nodes (ESP32/Raspberry Pi)

**Problem, concisely:** Deploy a distributed wireless mesh network of low-cost sensor nodes (tilt, vibration, displacement/strain, crack detection) over underground coal mine panels. Use AI/ML to detect abnormal ground deformation patterns and issue early-warning alerts via a GIS-based dashboard, with offline capability and periodic cloud sync.

**Skills required:**
- Embedded C/C++ (Arduino/ESP32) — sensor interfacing (I2C/SPI/analog)
- Basic electronics/wiring — node construction, power management
- LoRa/mesh networking (or WiFi mesh via `painlessMesh` as an easier fallback)
- Backend development (Python/Flask or Node.js) + database
- Frontend/web development (HTML/JS + Leaflet.js for the GIS map)
- Basic time-series statistics or scikit-learn for anomaly detection

**Pros:**
- Splits naturally into 6 distinct, non-overlapping ownership areas — ideal for a 6-person team
- Scales "for free" with team size: more people → more physical nodes → more convincing live mesh-resilience demo (e.g., kill a node mid-demo, show rerouting)
- All components are commodity/cheap (₹200–800 per sensor)
- Fully buildable, physically demonstrable end-to-end in hackathon timeframe
- ML bar can start simple (threshold-based) and scale up if time allows

**Cons / Challenges:**
- Many moving parts (embedded + networking + backend + frontend + ML) require coordination across the whole team
- True multi-hop mesh networking can be finicky to debug under time pressure
- Needs a physical demo rig (tiltable platform) to land the "wow" factor — easy to forget until late

**Traps to avoid:**
- Building only 2–3 nodes and calling it a "mesh" — too weak a demo to prove the concept
- Skipping the physical tilt-rig demo — without it, judges only see numbers, not the actual use case
- Over-investing in ML sophistication before the fusion logic and physical layer are solid
- Claiming offline-and-sync capability in the pitch without actually implementing it

---

### PS 26172 — Low Latency and Efficient Voice Activator for Edge Devices
**Organization:** ISRO | **Theme:** Miscellaneous | **Target HW:** ESP32 / Raspberry Pi

**Problem, concisely:** Build an ultra-lightweight keyword-spotting (KWS) model that runs locally under 256KB RAM and <10% idle CPU. On detecting a **custom** wake word (no pre-trained "Hey Google"-style keywords allowed), stream the following audio to a cloud ASR server with minimal latency. Open-source frameworks only (TensorFlow Lite for Microcontrollers, PyTorch Mobile, etc.).

**Skills required:**
- Python (TensorFlow/Keras or PyTorch) — model training
- Audio DSP fundamentals (MFCC/mel-spectrogram feature extraction)
- Embedded C/C++ (ESP-IDF or Arduino) — mic driver, inference loop
- Model quantization / TFLite Micro (int8 quantization to fit the RAM budget)
- Basic networking (sockets/MQTT) — the cloud handoff
- Dataset handling and augmentation (noise injection, pitch/time shift) to compensate for a small custom dataset

**Pros:**
- Narrow, deep problem — a 2-person core team (ML + embedded) can carry it entirely
- Cheap hardware (~₹400 for an ESP32), extensive tutorials and documentation
- Clear, measurable evaluation metrics (idle CPU%, RAM footprint, false-accept rate, latency) that translate directly into a strong demo
- Plays well to skillsets adjacent to DSP/quantization/embedded work

**Cons / Challenges:**
- Core loop is narrow — with 6 people, 4 can be under-utilized unless scope is deliberately expanded
- Custom dataset collection (samples + negatives + noise conditions) takes real time and discipline
- Quantization can noticeably hurt accuracy; may need quantization-aware training to recover it

**Traps to avoid:**
- Using any model pre-trained on generic assistant keywords ("Hey Google," "Alexa") — explicitly disqualified
- Shipping an uncompressed/heavy model that blows the 256KB ceiling
- Leaving half the team without a real role — deliberately assign extra members to rigorous validation (large benchmark dataset, false-accept/reject testing), multi-platform benchmarking (ESP32 vs. Pi Pico vs. another MCU), and a live metrics dashboard for the demo
- Treating this as "done" once the light turns on — the PS's actual evaluation criteria are the four measured metrics, not just detection working once

---

### PS 26049 — Reliability of Electrical/Electronic Systems in Ladakh HAA/SHAA
**Organization:** DRDO | **Theme:** Smart Automation

**Problem, concisely:** Ladakh's extreme cold (-35°C to -40°C), low atmospheric pressure, low oxygen, high UV/cosmic radiation, and large day-night thermal swings degrade electronics through seven distinct failure modes: reduced cooling efficiency, insulation breakdown/arcing, battery degradation, thermal-cycling solder fatigue, radiation-induced semiconductor/memory errors, and communication signal issues. The PS explicitly cites drone battery/motor drain (60min flight at sea level → ~20-25min in Ladakh) as its real-world example.

**Skills required:**
- Electronics/thermal design — battery pack and BMS-level knowledge
- Control systems basics (PID or bang-bang control loops) for thermal management
- Basic mechanical/materials understanding (insulation, enclosure design)
- Literature research and technical-methodology writing — needed for the failure modes you can't physically test

**Pros:**
- The PS itself hands you a scoping anchor: the drone battery example tells you exactly what a compelling, narrow demo looks like
- The battery-thermal-management subset is testable with normal resources (a household freezer or dry ice gets you to -20 to -30°C)
- Forgiving of literature-backed reasoning for untestable failure modes (low pressure, radiation) — honest scoping is respected more than overclaiming
- Uses a different skillset than 26025/26172, so it doesn't compete for the same team members if run as a 3rd option

**Cons / Challenges:**
- Broad list of seven failure modes tempts teams into shallow, scattered coverage
- Some effects (low-pressure dielectric breakdown, cosmic radiation damage) cannot be physically tested without specialized chambers

**Traps to avoid:**
- Trying to address all seven failure modes shallowly — this reads as a literature survey, not engineering work
- Claiming to have tested low-pressure or radiation effects without the equipment to back it up
- Not assigning someone to explicitly own the "how we addressed what we couldn't physically test" narrative — DRDO judges will specifically probe this

---

### PS 26185 — Helmet-Mounted Conformal Antenna for Tactical Comms
**Organization:** Ministry of Home Affairs (NSG) | **Theme:** Defence/Security | **Target HW:** Flexible conformal microstrip patch antenna (UHF & L-Band)

**Problem, concisely:** Design a low-profile, flexible, conformal microstrip antenna array integrated onto an NSG ballistic helmet, supporting dual-band (UHF + L-Band) operation for tactical radios and helmet cameras, with an RF shielding layer to protect the wearer while directing gain outward, connected via a ruggedized coax interface.

**Skills required:**
- Antenna theory (impedance matching, Smith charts, gain/directivity) — typically a junior/senior EM coursework topic
- EM simulation software: HFSS, CST (student license), or the free/open-source **openEMS**
- Flexible-substrate PCB fabrication (Kapton or flexible FR4)
- RF shielding layer design
- VNA-based validation (S11/return loss, impedance matching)

**Pros:**
- Narrower scope than the multi-subsystem PSs — it's "just" the antenna, not a full communications system
- If lab access exists, the simulate → fabricate → validate workflow parallels other EDA-style design flows

**Cons / Challenges (this is a hard access gate, not just a difficulty curve):**
- Requires an RF/antenna lab with a VNA — many colleges won't have this
- Antenna design theory is typically beyond sophomore coursework; needs a mentor or serious self-study
- Fabricating flexible substrates needs a PCB lab that supports flex-PCB work — not universally available
- No access to real NSG ballistic helmets; testing/integration claims will be on a generic mockup at best

**Traps to avoid:**
- Attempting to size antenna dimensions without simulation software — this will not produce a working design
- Overclaiming ballistic-integrity testing that was never actually performed
- Underestimating the difficulty of stacking dual-band + conformal + shielding requirements simultaneously — each alone is nontrivial

**Conditional verdict:** Only move this above 26049 if your college has genuine RF lab access **and** at least one team member with antenna theory background. Without both, it should not be a serious option.

---

### PS 26026 — Quadruped/Handheld Detection of Narcotics & Explosives (Indian Railways) — RED FLAG
**Organization:** Ministry of Railways | **Theme:** Robotics & Drones

**Problem, concisely:** Build an AI-enabled mobile quadruped robotic platform and a handheld device for real-time detection of narcotics (heroin, cocaine, meth, cannabis derivatives, etc.) and explosives (RDX, TNT, PETN, TATP, C4, etc.) across railway stations, platforms, coaches, and yards — including LiDAR-based SLAM navigation, thermal/optical imaging, facial recognition, and secure real-time communication to control centres.

**Skills that would be required (for reference only — not recommended to pursue):**
Legged robotics control, LiDAR SLAM, sensor fusion, computer vision (facial recognition, thermal imaging), spectrometry/chemical sensing, secure communications/encryption, mechanical design.

**Why this is a structural red flag, not just "hard":**
- **Legal/safety barrier:** students cannot legally possess real narcotics or explosives to calibrate a detector against — any demo either fabricates results or uses unverified surrogate compounds
- **Hardware cost:** real narcotics/explosives detection needs Raman spectroscopy or ion-mobility spectrometry hardware costing several lakhs to tens of lakhs of rupees — not a "build it cheaper" problem, it's a physics-of-sensitivity problem
- **Quadruped robotics is a multi-year problem on its own:** dynamic balance and gait control is a control-systems research area; commercial platforms cost lakhs
- **Five hard subsystems stapled together:** mobility + spectrometric detection + facial recognition + secure comms + autonomous navigation — no realistic team integrates all five in hackathon time
- **Rescoping erases the PS:** any workable version (wheeled robot, gas-sensor proxy, simulated targets) stops being a genuine answer to what was actually asked

**Traps to avoid (if pursued anyway):** fabricating/faking detection results in the demo; underestimating quadruped platform cost; presenting a rescoped wheeled-robot version as if it fulfills the original PS without clearly flagging the substitution; ignoring facial recognition's privacy/legal implications.

---

### PS 26050 — High Altitude Performance Optimization of Anti-Drone Systems — RED FLAG
**Organization:** DRDO | **Theme:** Robotics & Drones

**Problem, concisely:** Harden an existing anti-drone system (detection, tracking, neutralization — spanning RF, electro-optical, mechanical, and stabilization subsystems) to maintain micro-radian pointing accuracy under Ladakh's extreme cold, low pressure, dust, and high-wind conditions, including compensation for temperature-induced cable rigidity and structural deformation.

**Skills that would be required (for reference only — not recommended to pursue):**
Precision controls/mechatronics (4th-year/graduate level), thermal-structural FEA (ANSYS/COMSOL/CalculiX), adaptive control algorithms (e.g., Kalman filtering), environmental qualification methodology (MIL-STD-style thinking) — plus everything needed to build or credibly simulate an anti-drone system in the first place.

**Why this is a structural red flag, not just "hard":**
- **Hidden prerequisite:** the PS assumes a working anti-drone system already exists — you'd effectively need to solve 26026-level system integration first, before addressing what's actually asked
- **Precision control requirement exceeds undergrad coursework:** maintaining micro-radian pointing under thermal/structural stress is typically 4th-year or graduate-level controls
- **Validation equipment is essentially inaccessible:** thermal chambers reaching HAA/SHAA temperatures, low-pressure chambers, dust ingress rigs, wind-load benches — no realistic field test is possible without this
- **Elevated rigor bar:** as a DRDO/IDEX PS, judges expect qualification-methodology reasoning (component derating, MIL-STD-style validation), not a hobbyist demo
- **Best-case realistic outcome is simulation-only:** even with a well-scoped single-subsystem focus (e.g., gimbal pointing under simulated thermal drift), the ceiling is a rigorous methodology/simulation submission — not a working, field-tested demo

**Traps to avoid (if pursued anyway):** attempting to physically build and field-test the full system; presenting simulation results as though they were physically validated; underestimating that a credible demo requires solving the base anti-drone system first.

---

## 3. Why the Bottom Two Are Categorically Different From the Rest

For PS 26025, 26172, 26049, and 26185, the hard parts are things effort, planning, or lab access can genuinely solve — more team members, more testing time, better scoping, or securing lab access closes the gap.

For PS 26026 and 26050, the hard parts are **structural**: legal barriers to possessing real narcotics/explosives, hardware costs in the lakhs-to-crores range, prerequisite systems (quadruped robots, full anti-drone platforms) that are themselves multi-year engineering efforts, and validation equipment (spectrometers, HAA/SHAA environmental chambers) that doesn't exist at most universities regardless of team size or effort. That is the line between "difficult — pick if your team is prepared" and "red flag — avoid regardless of team strength."

## 4. Recommended Path Forward

1. **First choice: PS 26025** — best team-size fit, fully buildable, real physical demo achievable.
2. **Second choice: PS 26172** — plays to a concentrated ML/embedded skillset; expand scope deliberately (validation rigor, multi-platform benchmarking, live metrics dashboard) to use all 6 team members well.
3. **Third choice (backup): PS 26049** — genuinely buildable if scoped to the battery-thermal-management angle; different skillset from the top two.
4. **Conditional fourth choice: PS 26185** — only if your college has RF/antenna lab access and EM theory background on the team.
5. **Do not shortlist PS 26026 or PS 26050** unless no other option remains — both carry structural barriers no amount of team effort resolves within a hackathon timeframe.
