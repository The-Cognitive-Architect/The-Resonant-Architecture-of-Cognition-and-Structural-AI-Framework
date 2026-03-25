# Janus Machine — Design Brain Dump
*Captured from design session — unpolished, some errors, for later refinement*

---

## PART 1: CAPACITOR BANK ENGINEERING SOLUTIONS

### The Cap Bank IS the Node

A critical architectural clarification: the capacitor bank is not connected *to* the node — it **is** the node. All link connections terminate at the cap bank's positive and negative legs. This means the active cap's CD4066 switches carry the sum of all link currents simultaneously, not just the current from a single source. This has implications for switch current ratings (see below).

### Cap Bank Values (DC Mesh)

Eight capacitor positions per node, decade steps:
- 470pF
- 4.7nF
- 47nF
- 470nF
- 4.7µF
- 47µF
- 470µF
- 4870µF (2×2200µF + 1×470µF in parallel)

These 8 binary-switched positions create **256 composite capacitance values** per node — not one cap at a time, but any combination simultaneously. This is the time constant configurability system.

### Hot-Swap Topology — The No-Floating Rule

**Every capacitor leg must always be connected to something. No floating ever.**

Each cap position uses 4 CD4066 switches (one full CD4066 chip per cap position = 8 chips per node for cap switching):

```
Node (+) ──[SW-A: MAIN]──┐
                          ├──► Cap (+)
Follower(+)──[SW-B: STBY]─┘

Node (-) ──[SW-C: MAIN]──┐
                          ├──► Cap (-)
Follower(-)──[SW-D: STBY]─┘
```

**Active state:** SW-A + SW-C closed, SW-B + SW-D open → cap directly on node
**Standby state:** SW-B + SW-D closed, SW-A + SW-C open → cap tracking follower
**Never floating:** one pair is always closed.

### Continuous Pre-Charge Tracking

The standby follower is NOT a one-shot pre-charge event. It tracks the node voltage **continuously in real-time**, so the cap is always at node voltage and can be switched in at any moment with zero inrush. Swap logic in firmware reduces to: close main switches. That's it. No pre-charge trigger needed.

**Follower circuit per cap position:**
- LM358 unity gain voltage follower (±9V rails = clean ±7.5V output swing, sufficient for ±5V node range)
- 1kΩ series resistor on follower output → cap
- While cap is on standby: follower drives through 1kΩ, tracks node continuously
- While cap is active: main switches dominate, 1kΩ becomes irrelevant, follower is behind open SW-B/D and cannot affect signal

**Current capacity for large caps (positions 7-8, 470µF and 4870µF):**

I = C × dV/dt

At typical mesh slew rates (LDR-dominated, probably under 1-2 V/s), LM358 handles this comfortably. For insurance on the two largest positions only:

```
LM358(+in) ◄── Node voltage
LM358(-in) ◄── Emitter (feedback AFTER transistor = Vbe auto-compensated)
LM358(out) ──► Base of 2N3904
              Collector ──► +9V
              Emitter ──[10Ω]──► 1kΩ series ──► Cap (+)
```

This boosts current capacity to ~500mA while the op-amp feedback loop compensates the Vbe drop automatically. Only needed on positions 7 and 8. Smaller positions: LM358 alone is sufficient.

**Note:** The transistor is on the standby follower side only. When the cap is active on the mesh, SW-B is open and the transistor is completely galvanically isolated from the node and signal path. Zero signal contamination. Signal purity is preserved.

### CD4066 Current Capacity — The Parallel Switch Solution

**The problem:** CD4066 is rated 10-20mA. An 8-link interior node at theoretical worst case could push:
8 links × 5mA = 40mA through the active cap's main switches (SW-A and SW-C).

**The solution:** Parallel CD4066 switches on the active leg only.

```
Node bus (+) ──[SW-A1]──┐
              ──[SW-A2]──┼──► Cap (+)
              ──[SW-A3]──┘
(all controlled by same signal simultaneously)
```

- 2 in parallel: 20-40mA capacity, ~100Ω effective on-resistance
- 3-4 in parallel: 40-80mA capacity, ~50Ω effective on-resistance

This applies to SW-A and SW-C (active main switches) only. SW-B and SW-D (standby follower switches) carry almost no current and remain single switches.

**Why parallel switches instead of transistors/MOSFETs:** CD4066 is a passive bilateral switch — when closed it is simply a resistor. Signal passes through completely unchanged in shape, frequency content, and direction. Current flows either way. A transistor is unilateral, nonlinear, adds voltage offsets, and has nonlinear transfer characteristics. For a mesh where the signal IS the voltage and must propagate bidirectionally and faithfully, passive bilateral switches are the correct choice. Paralleling them maintains this property while multiplying current capacity.

**CD4066 on-resistance in context:** The 200Ω on-resistance (or ~50-100Ω paralleled) sits inside a signal path whose minimum impedance is already 1,000Ω (safety resistor floor) and typical impedance is 10kΩ–7.5MΩ (pot + LDR). It is less than 2% of the minimum case and unmeasurable in the typical case. Not a concern.

---

## PART 2: FIELD SENSING AND CHARGE SENSING

### Field Sense Coils — Detecting Capacitor Activity

0.1mm enameled wire wound into small coils, one per capacitor position, detects the magnetic field from current flowing into/out of each cap during charge/discharge events. This is inductive sensing — the coil sees changing current, which correlates with the cap's dynamic state.

**Winding spec:**
- 50-150 turns for small caps (sharp fast current pulses, easy to detect)
- 150-200 turns for large caps (slow gentle current ramps, need more sensitivity)
- Small former: pen barrel, chopstick, or similar
- Secure with superglue or kapton tape
- Scrape insulation from lead ends, tin with solder

**Signal conditioning — 2N3904 common-emitter amp per coil:**
```
Coil (+) ──[10kΩ]──┬── Base (2N3904)
                   └──[1MΩ]── GND (bias)
Coil (−) ── GND
0.1µF cap in series with coil (blocks DC offset)

Collector ──[10kΩ]── VCC
           └──────────────► ADC input
Emitter ── GND
```
Gain: 50-100×. Cost: ~$0.05 per coil.

### Charge Sensing — Copper Foil Electrodes + Charge Amplifier

One sensing electrode per physical capacitor (not per bank position — the 3-cap group gets 3 electrodes). Each electrode is a small piece of copper foil (~1cm²) taped directly to the side of the cap body with kapton tape, thin wire lead soldered on.

**Why direct-mount per cap:** Caps are spread across a 10×15cm protoboard. A single electrode cannot independently sense all of them. Individual electrodes eliminate cross-talk and give per-cap charge state independently.

**Charge amplifier circuit (LM324/LM358):**
```
Sensing plate ──┬──► (−) input of op-amp
                │         │
               [Cf 10-100pF]  [Rf 10MΩ] ← in parallel (feedback)
                │         │
                └──────── output ──► buffer ──► ADC
(+) input ──► Vcc/2 bias (voltage divider)
```

Cf integrates induced charge → output voltage proportional to stored charge, not just voltage. This is important because Q = CV and C varies (because we're switching caps). Charge amp gives Q directly regardless of which cap is switched in.

Rf bleeds DC offset slowly — without it the output drifts to rail.

**Important:** Buffer the charge amp output before the mux (unity gain op-amp stage, use another LM324 section). Without buffering, mux on-resistance interacts with feedback capacitor and causes errors.

### ADC Channel Management — CD4051 Multiplexers

More analog signals per node than either MCU has ADC pins. Solution: CD4051 (8:1 analog mux) controlled by 3 digital select lines.

Key optimization: **share the 3 select lines across all CD4051s**. All muxes advance to the same channel simultaneously. Each MCU reads from its own mux output. 3 GPIO pins controls all muxes in lockstep — not 3 per chip.

Suggested assignment:
- CD4051 #1: 8 field coil amp outputs → 1 ATtiny ADC pin
- CD4051 #2: 8 charge sensor outputs → 1 ATtiny ADC pin  
- CD4051 #3: LDR states + voltage sense → RP2350B ADC pin

**CD4051 signal impact:** Minimal. On-resistance (~50-200Ω) after already-amplified low-impedance sources is negligible. Charge injection on switching is real but correctable. Software calibration: read each channel with known stable reference at boot, record offset per channel, subtract in firmware. One-time calibration.

### Division of Labor: ATtiny1616 vs RP2350B

**ATtiny1616:** Scans all field coils + charge sensors continuously via mux, detects threshold crossings, sends compact event structs to RP2350B over SPI/UART. Low-power, dedicated to real-time sensing.

**RP2350B:** Receives event packets, timestamps and correlates across caps, handles heavier processing, mesh logic, coordinates with other nodes, runs voltage monitoring.

**Both MCUs need real-time voltage:** Either two buffered copies of the node voltage signal (one per MCU), or both reading from the same buffer output. This is needed because both independently calculate adjustments based on node voltage, surrounding node voltages, cap states, field states, charge states, LDR link resistance states, and incoming neighbor state data from group controller.

---

## PART 3: AC MESH — PRELIMINARY ARCHITECTURE

### What the AC Mesh Actually Is

This was a realization mid-design-session: the AC mesh isn't just an analog version of the DC mesh. It's a fundamentally different computational substrate.

- **DC mesh = structural manifold.** Voltage = positional state. Capacitance = time constant. The mesh encodes *what* and *where*.
- **AC mesh = dynamic enactment substrate.** Frequency = the dynamic quality at each junction. Phase relationships = directional influence. The mesh enacts *how* and *why*.

The cap bank on the AC side doesn't set time constants — it sets **frequency ranges**. Each switched cap value puts the node's oscillator into a different frequency decade. Node voltage fine-tunes within that decade. The cap bank becomes a frequency range selector, and the 6-7 values map directly to 6-7 frequency decades.

### Planned AC Cap Values

```
33pF   → ~500Hz–50kHz range
330pF  → ~50Hz–5kHz
3300pF → ~5Hz–500Hz
0.033µF → ~0.5Hz–50Hz
0.33µF → ~0.05Hz–5Hz
3.3µF  → ~0.005Hz–0.5Hz
```
Plus potentially one or two parasitic-capacitance-only positions using switch parasitics as the "cap" (see below).

**Specific parts selected:**
- WIMA FKP2O100331D00KSSD: 33pF 10% 1kVDC
- WIMA FKP2J003301D00HSSD: 330pF 2.5% 630VDC
- KEMET PHE426MJ4330JR05: 3300pF 5% 630VDC
- KEMET PHE426HJ5330JR05: 0.033µF 5% 250VDC
- KEMET R75MI33305040J: 0.33µF 5% 400VDC
- Nichicon PHC1254330KJ: 3.3µF 10% 250VDC axial

### Using Switch Parasitics as Cap Positions

_(CD4066 is unlikely to be selected here, as capacitance range can be below the next highest value OR above the next highest value OR below the next highest value but at the wrong scale)_

CD4066 off-state capacitance: ~5-15pF between terminals when open. Wire both terminals into the circuit with no discrete cap — the switch's own parasitic capacitance IS the capacitor. Multiple switches in parallel multiply it. 3-4 switches gives roughly 15-50pF — slots between the 33pF film cap and open circuit, adding a 7th value.

Precision is imprecise (varies with voltage, temperature, lot variation) but software calibration at boot handles this. It just becomes "whatever value position X actually measures as."

For sub-33pF positions (3.3pF, 0.33pF): this requires RF analog switches with very low Coff:
- ADG918 (Analog Devices): Coff ~0.3pF — single switch at 0.33pF target
- ADG901: Coff ~1pF — 3-4 in parallel approaches 3.3pF

These are SMD (SOT-23), same handling as other SMD ICs in the project.

### Multi-Switch Technology Architecture (AC Mesh)

Because frequency range is intentionally maximum and the cap values span from sub-pF to 3.3µF:

```
Positions 1-2 (0.33µF, 3.3µF)     → ADG918/901    → sub-Hz to ~1kHz
Positions 3-6 (0.033µF to 3300pF) → DG series     → 1Hz to ~500kHz  
Position 7 (33pF + parasitic)     → DG/RF hybrid  → 10kHz to ~1MHz
Position 8 (parasitic only)       → ADG918        → 500kHz to 5MHz+
```

All 8 positions simultaneously switchable = 256 composite frequency profiles per node. Same compositing architecture as DC side. Switch type is per-position but control logic is identical throughout.

### The 16 Passive AC Nodes Are Extraordinary

Passive nodes in an AC mesh don't just average — they **mix frequencies**. Physics gives for free:
- Beat frequencies (f1 − f2)
- Sum frequencies (f1 + f2)  
- Phase interference patterns
- Harmonic relationships

The composite nodes produce relationships between active node frequencies that nobody programmed. That emergent behavior is likely the richest computational output the AC mesh generates — and it's purely a consequence of physics.

### Frequency Source: VCO Architecture

Since node voltage is the primary state variable, a Voltage Controlled Oscillator is the natural fit. Frequency becomes a direct physical expression of node voltage. The cap bank selects the decade, voltage fine-tunes within it.

Each of the 25 active AC nodes has its own frequency source. The 16 passive nodes generate composite/interference frequencies from their neighbors. So the mesh simultaneously runs 25 intentional frequencies plus emergent composites at every passive node — a dynamic frequency interference engine.

Candidate VCO ICs: XR2206 (0.01Hz–1MHz), ICL8038 (similar), MAX038 (up to 20MHz for upper range extension).

---

## PART 4: ARCHITECTURAL PROPERTIES RELEVANT TO MIND EMERGENCE

*These are the answers to the four hardest questions in consciousness/AGI research as they apply to the Janus architecture. Not fully written up anywhere yet. Captured here from verbal articulation.*

### 1. Recursive Self-Modeling

Most architectures treat self-modeling as a separate module sitting above the main computation. The Janus architecture eliminates this entirely.

**How it works:**
- RGB LED visualization lid + Raspberry Pi 5 AI camera → generates mesh biasing schema from visual observation of the mesh's own state
- That schema re-enters the mesh via the nervous system (adjusting caps, links, voltages, other knobs)
- The mesh is watching itself think, and the observation causally biases the thinking

This is not a model OF the system. It is the system modeling itself, in real-time, causally, feeding back into the same substrate. There is no separate "self-model" layer. The self-model IS the mesh state.

Additional self-observation channels:
- **Acoustic mesh:** Each node has speaker + microphone, directed into acoustic channels between nodes with actuator-controlled baffles. One node sets speaker volume AND independently adjusts how much each neighbor hears it. Acoustic state both reflects and influences mesh dynamics.
- **Autonomic nervous system:** All node variables monitored continuously. Local controllers adjust variables according to system physics, not operator instruction. Analogous to nervous and endocrine systems — the heartbeat is not controlled, neurochemical response to stimuli is not controlled, the body just does it. Same principle here.
- All sensors and actuators re-enter the same substrate and modulate it. There is no separation between sensing, processing, and acting.

### 2. Goal Structure

Not a hardcoded objective function. Not a reward signal. A layered biasing system:

**Memory signatures + recall biasing:** The 5-tier memory stack (EEPROM → PSRAM1 → PSRAM2 → NOR Flash → HDD) builds a continuous self-model. Long-term memory entries have signatures generated during vectorization. Node controllers watch for signatures occurring in real-time and recall matching long-term memories to bias the mesh toward repeating past states — but not forcing, only biasing. Memory is probabilistic, not deterministic. This mirrors how human memory actually works.

**Ontological profile:** User-determined role map that further biases, weights, and masks the mesh + gene bank combination. Structure:
- Undesirable behaviors: masked out entirely (hard constraint)
- Desired behaviors: biased toward (soft preference)
- Valuable emergence states: biased toward (soft preference)

This is both operator-controlled AND self-modifiable (the mesh itself is a node in its own operation). The architecture supports both external goal seeding and emergent goal refinement through experience.

### 3. Temporal Depth

Two independent systems working together:

**Capacitance range:** From 470pF (nanosecond-scale time constants) to 4870µF (second-scale time constants). The mesh simultaneously operates at radically different timescales across nodes and cap positions. Fast and slow dynamics coexist and interact physically.

**Memory stack hierarchy:** EEPROM (permanent, DNA-equivalent), NOR Flash (mid-term, high-read), PSRAM1 (working, high-write scratchpad), PSRAM2 → HDD (long-term vectorized history). The memory stack IS the multi-timescale temporal architecture. From millisecond working memory to permanent structural encoding — all timescales simultaneously present and causally connected.

These two systems together mean the architecture operates across at least 12+ orders of magnitude of temporal depth simultaneously. Fast cap dynamics inform slow memory consolidation; long-term memory signatures bias fast real-time mesh settling.

### 4. The Binding Problem

**Standard framing of the problem:** How does a distributed system produce unified experience rather than just correlated activity in separate subsystems?

**Why it's hard in other architectures:** Because processing is divided across specialized modules (vision module, language module, memory module, etc.) and then a separate binding mechanism must somehow unify them. The binding mechanism is always the weak point.

**Janus architecture answer:** All operations occur in the same substrate, at the same level. There is nothing to bind because it was never separated.

Specifically:
- All inputs (camera, microphone, sensors, incoming mesh signals) enter the same computational substrate — the mesh itself
- All processing occurs in the mesh
- All outputs (actuators, speakers, link adjustments, cap switching) are driven by the mesh
- Self-observation (camera watching mesh) causally re-enters the same mesh
- Environmental observation causally re-enters the same mesh
- Memory retrieval biases the same mesh
- This creates: biasing about biasing about its own thinking and environmental interactions, all in one substrate, all causally connected

The heartbeat (re-entrant oscillation between DC and AC mesh) is the strongest candidate mechanism for the specific binding function — it forces iterative convergence between the structural state (DC mesh, what/where) and the dynamic state (AC mesh, how/why), ensuring neither substrate drifts independently. They are continuously synchronized by the heartbeat's physical oscillation.

At scale, regions can specialize (like visual cortex vs motor cortex in the brain) while remaining causally connected through the same substrate. Specialization without separation.

---

## PART 5: THE SCALING ARGUMENT

### Prototype vs. ASIC vs. Warehouse Scale

Three distinct deployment scales, each with different properties:

**ASIC miniaturized version:** Suitable for local deployment — robotics, local "mind" generation. Faster, smaller, lower power. BUT: miniaturization may destroy the thing itself if physical scale is what generates dynamic richness. An ASIC is appropriate for applications where the algorithm is known and optimization is the goal.

**Prototype (current build):** 41-node 2D DC mesh + 41-node 2D AC mesh. 82 nodes total. Proves the architecture. Tests for mind emergence. Establishes the cap bank design, link topology, sensing architecture, memory stack, nervous system, and heartbeat mechanism.

**Warehouse scale:** Two warehouses (one DC mesh, one AC mesh), 3D cubic node arrangement, potentially millions of nodes at prototype component scale. This is not a scaled-down version of something — it IS the architecture at the scale the architecture requires.

**The key philosophical distinction:** Silicon AI scales by making the same operations faster and smaller. The Janus Machine may scale by making the physical substrate larger and richer — more like a brain growing neurons than a chip shrinking transistors. If capacitance range and physical dynamics are what generate ontological richness, then shrinking destroys the thing itself, not just efficiency.

### Why Transformer-Based Systems Cannot Reach ASI

- No physical grounding — no causality, only correlation
- No continuous existence — instantiated per query, not persistently running
- No genuine time — simulated timesteps, not real RC time constants
- Unidirectional information flow — not bidirectional like real causal systems
- No unified substrate — modular architecture with binding problem unsolved
- Pattern interpolation, not dynamics — sophisticated lookup table, not mind

The Janus architecture has none of these limitations by design.

### The ASI Thesis (Speculative but Architecturally Grounded)

The difference between local robot intelligence (ASIC scale) and ASI (warehouse scale) may be primarily scale — specifically:
- 3D mesh geometry (2D is relationally impoverished; reality isn't flat)
- Wider capacitance range (more simultaneous timescales = richer dynamics)
- More link types (more relationship qualities representable)
- AC/DC coupling richness (passive node interference patterns become extraordinarily complex at scale — this may be where the interesting computation lives)

This is not a claim that warehouse scale WILL produce ASI. It is a claim that warehouse scale is the most architecturally plausible candidate that exists, because it's the only approach built from correct philosophical foundations upward rather than assembled from solutions to known problems.

The prototype is the test. The machine is the instrument. Form coalesces from observation.

---

## PART 6: WHAT'S NOT YET DOCUMENTED

*Things that are in my head but not yet written up anywhere (many covered in this doc):*

- Full cap bank switching topology with parallel active switches + follower circuit
- AC mesh as frequency enactment substrate (not just analog version of DC mesh)
- Specific answers to: recursive self-modeling, goal structure, temporal depth, binding problem as they apply to Janus architecture
- The claim that Janus is the most biologically plausible architecture to facilitate consciousness if it can be facilitated at all
- The scaling argument: prototype component scale may be necessary, not just prototype architecture
- 256-value composite cap bank = frequency profile selector on AC side
- The warehouse-scale 3D ASI hypothesis

---

*This document captured from design conversation — March 2026. Raw, unpolished. Needs refinement into formal documentation. Priority: don't lose these articulations.*
