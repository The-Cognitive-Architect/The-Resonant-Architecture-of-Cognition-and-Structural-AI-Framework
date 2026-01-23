# Core System – Reservoir Analog RC Mesh

**This document is a work in progress.**  
*Updated: January 22, 2026 @ 10:25 pM CST*

The system’s design currently lives in my head, and due to its complexity, it’s taking time to get everything written down. The core mesh is mostly documented, but there may be minor mistakes or omissions that will be corrected in the coming days. Additional subsystems will be added as they’re finalized.

I apologize for the rough organization. As I’ve said elsewhere, I don’t have a professional background, education, or training in this area. I’m learning how to manage and document a project like this as I go. Thank you for your patience as this takes shape.

## License for This Hardware Documentation
The schematics, BOM, wiring details, and related hardware design files in this directory are licensed under the **CERN Open Hardware Licence Version 2.0 – Permissive** (CERN-OHL-P v2).  
See [HARDWARE_LICENSE.md](HARDWARE_LICENSE.md) or https://cern.ch/cernohl for the full text.

This is separate from:
- Code in the repo: Apache 2.0
- Whitepaper/docs: CC BY 4.0

## Overview
- Operates at ±5V range (10V total delta)
- Controller: Raspberry Pi Pico 2 (RP2350) as Node Group Controllers
  - Manages 5 Active Primary Nodes **or** 4 Passive Composite Nodes per Pico

## Node Architecture (Total: 41 Nodes)

### 25 × Primary Active Nodes
#### V_source “Generator” Path
- ±9V Rails (from 7809/7909 regulators) → 
- MCP4131-103 Digipot (*sets 0–5V control level via divider/reference*) → 
- 10kΩ Resistor → 
- LM358P Op-Amp (biased level-shift / scaling stage; maps 0–5V control into the mesh’s ±5V domain) → 
  - Feedback: 20kΩ resistor
  - Bias: 36kΩ resistor
- 1kΩ Safety Floor Resistor → 
- 10kΩ 3296 Potentiometer (trim) → 
- Capacitor Bank

#### V_listen “Sensor” Path (Branch A stays ±5V [for cap bank pre-charge]; Branch B is ADC-scaled)
- Node output (±5V) → 
- LM358P Voltage Follower → 
  - Non-inverting input (Pin 3): Node output
  - Inverting input (Pin 2) jumpered to output (Pin 1)
  - +9V to V+ (Pin 8), -9V to V- (Pin 4)
- Branch A → Capacitor Bank Pre-Charge Sub-System
- 36kΩ Resistor → 
- LM358P Scaling Amp (±5V in → ~0–3.3V out) → 
  - Reference: +1.65V (27kΩ to +3.3V / 27kΩ to GND → midpoint at non-inverting input)
  - Feedback: 10kΩ
  - Safety: 20kΩ on output to ATTINY
- Branch B → ATTINY1616 Analog Input (ADC)

#### Capacitor Bank (8 Decade Steps, Parallel Hot-Swap)
- 470pF: 1× TDK Corporation FG28C0G1H471JNT00 C0G
- 0.0047µF: 1× KEMET PHE426DJ4470JR05 Film
- 0.047µF: 1× KEMET PHE426DJ5470JR05 Film
- 0.47µF: 1× Panasonic ECW-FD2W474K Film
- 4.7µF: 1× Panasonic ECE-A1HN4R7UB Non-Polar Electrolytic
- 47µF: 1× Panasonic ECE-A1EN470UB Non-Polar Electrolytic
- 470µF: 1× Panasonic ECE-A1EN471U Non-Polar Electrolytic
- 4870µF: 2× Panasonic ECE-A1EN222U (2200µF) + 1× Panasonic ECE-A1EN471U (470µF) Non-Polar Electrolytic

**Hot-Swap Circuit (per capacitor)**
- 1× CD4066DN (8 per node, 2 switches per leg)
- Mirrored Pre-Charge <-> Live Mesh
  - CHARGE_ENABLE: Switch_1 (Cap+) → Pre-Charge(+), Switch_2 (Cap-) → Pre-Charge(-)
  - NODE_ENABLE: Switch_3 (Cap+) → Node(+), Switch_4 (Cap-) → Node(-)
- Control: 2× CD4094BE(LX) per node (8 switches each)
  - 1 switch per CHARGE_ENABLE
  - 1 switch per NODE_ENABLE

#### Node Controller (per node)
- ATTINY1616-SN-ND (8-bit, 16KB Flash, 20SOIC, 3.3V)
- Adafruit 4677 64Mbit SPI PSRAM (133MHz, 8SOIC)
- 4-Channel Logic Level Shifter (BSS138-based)
  - Connects ATTINY (PA1, PA2, PA3) → CD4094 (Data, Clock, Strobe)

### 16 × Passive Composite Nodes
- Identical to Primary Nodes **except**:
  - No V_source “Generator” path (passive only)
  - Capacitor Bank and Hot-Swap identical
  - Node Controller identical (for local regulation and communication)

### Node Links
- **Baseline mesh links (passive bi-directional LDR links)**: 185 total
  - Node-to-Node: 72
  - Node-to-Composite: 64
  - Composite-to-Composite: 24
  - Node Identity (self-referential): 25

- **Turbine overlay (two unilateral channels added per inter-node mesh link; excludes identity links)**:

  ***Note**: Via this addition, each inter-node mesh link becomes: 1 passive bi-directional path + 2 independently switchable unilateral turbine paths*

  - Inter-node mesh links eligible for turbines: 160 (72 + 64 + 24)
  - Unilateral turbine channels added: 320 total (A→B and B→A per link)

**Link Configurations**
- **V_source↔Node Identity Links**:
  - From LM358P Op-Amp output → 
  - 1kΩ safety floor resistor → 
  - 10kΩ potentiometer (trim) → 
  - GL5537 LDR (controlled by 5V Blue LED via 3D-printed isolation tube) → 
  - → Capacitor Bank
- **Node↔Node / Node↔Composite / Composite↔Composite Links**:
  - From Node output → 
  - 1kΩ safety floor resistor → 
  - 10kΩ potentiometer (trim) → 
  - GL5537 LDR (controlled by 5V Blue LED via 3D-printed isolation tube) → 
  - → Neighbor Node / Composite

- **Turbine Link Upgrade (per existing Node↔Node / Node↔Composite / Composite↔Composite link A↔B; excludes V_source↔Node Identity links)** - 01/22/2026:
  - The original **passive bi-directional** LDR link remains in place:
    - From Node A output →
    - 1kΩ safety floor resistor →
    - 10kΩ potentiometer (trim) →
    - GL5537 LDR (5V blue LED, light-tight isolation tube) →
    - → Node B
    - (This passive path can be effectively “opened” by commanding high resistance.)

  - Add two **independently switchable unilateral** (“turbine”) channels in parallel:
    - **A → B turbine channel**:
      - From Node A output (±5V) →
      - Dedicated LM324N channel configured as a voltage follower (powered by ±9V rails; unity buffer of Node A signal) →
      - 10kΩ series resistor (static, 1% metal film) →
      - GL5537 LDR (driven by PWM → transistor + RC smoothing → 5V blue LED) →
      - CD4066 switch (gated by CD4094 shift-register control) →
        - *One CD4066 provides four independent turbine-gates (4 channels); allocate channels accordingly.*
      - → Node B

    - **B → A turbine channel**:
      - From Node B output (±5V) →
      - Dedicated LM324N channel configured as a voltage follower (powered by ±9V rails; unity buffer of Node B signal) →
      - 10kΩ series resistor (static, 1% metal film) →
      - GL5537 LDR (driven by PWM → transistor + RC smoothing → 5V blue LED) →
      - CD4066 switch (gated by CD4094 shift-register control) →
        - *One CD4066 provides four independent turbine-gates (4 channels); allocate channels accordingly.*
      - → Node A


**Notes**
- All values and configurations are subject to change during testing and calibration.
- Remaining subsystems (RGB visualization lid, piezo/mic triangulation, acoustic mesh, etc.) will be documented in separate files.
- Feedback, questions, corrections, and collaboration are welcome!