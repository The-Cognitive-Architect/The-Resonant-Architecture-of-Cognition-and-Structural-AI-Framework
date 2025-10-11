# The Resonance Chamber
# A Python embodiment of the cognitive-ontological framework presented in the source documents.
# © Anthony Janus 2025. This program is a symbolic interpretation and not for clinical or diagnostic use.

import time
import random
import textwrap
import sys
import os

# --- Configuration & Thematic Styling ---

# Enables Windows support for ANSI escape codes for color.
os.system('')


class style:
    """Class to hold color and style codes for console output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'

    # Colors
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GREY = '\033[90m'


def slow_print(text, delay=0.02, style_code=style.WHITE):
    """Prints text character by character for a narrative effect."""
    for char in text:
        sys.stdout.write(style_code + char + style.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def wrap_print(text, style_code=style.GREY, width=80):
    """Wraps text and prints it slowly."""
    wrapped_text = textwrap.fill(text, width=width)
    slow_print(wrapped_text, delay=0.01, style_code=style_code)

# --- Core Framework Constructs ---


class Stimulus:
    """
    Represents a task, idea, or external demand.
    This is the "fuel" for the Resonance Engine. Its primary attribute is 'coherence'.
    """

    def __init__(self, name: str, coherence: float, complexity: int, is_imposed: bool):
        self.name = name
        # Coherence (0.0 to 1.0): The degree of meaning, integrity, and authenticity.
        self.coherence = max(0.0, min(1.0, coherence))
        # Complexity (1 to 10): Affects the output of a Meaning Storm.
        self.complexity = complexity
        # Is Imposed: True if it's a non-negotiable external demand.
        # This is a key trigger for False-Structure Intolerance (FSI).
        self.is_imposed = is_imposed

    def __repr__(self):
        return f"Stimulus(Name: {self.name}, Coherence: {self.coherence:.2f}, Imposed: {self.is_imposed})"


class ResonanceEngine:
    """
    The core symbolic engine embodying the cognitive architecture.
    It operates based on the principles of OMEF, FSI, and SCMF.
    """

    def __init__(self):
        # Personality Profile (Metaphorical Representation)
        # These are not clinical, but symbolic tuners for the engine's behavior.
        self.profile = {
            # Exceptionally low, requiring resonance (OMEF)
            "industriousness": 0.03,
            "volatility": 0.97,       # Exceptionally high, powers the FSI veto
            "openness": 0.96,         # High, drives curiosity and meaning storms
        }

        # State-Contingent Motivational Filtering (SCMF)
        self.state = "IDLE"  # Can be IDLE, RESONATING, or STALLED
        self.energy = 50.0   # Current energy level (0-100)
        # A random value representing the current deep interest
        self.ontological_focus = random.random()
        self.state_timer = 0  # How long the engine has been in its current state

    def _get_status_display(self):
        """Returns a styled string representing the current engine state."""
        if self.state == "IDLE":
            return f"{style.BLUE}[IDLE]{style.RESET} Energy: {self.energy:.0f}% | Focus: {self.ontological_focus:.2f}"
        elif self.state == "RESONATING":
            return f"{style.GREEN}[RESONATING]{style.RESET} Energy: {self.energy:.0f}% | Focus: {self.ontological_focus:.2f}"
        elif self.state == "STALLED":
            return f"{style.RED}[STALLED]{style.RESET} Energy: {self.energy:.0f}% | System Integrity Compromised"
        return ""

    def introduce_stimulus(self, stimulus: Stimulus):
        """The main interaction point. The engine processes a stimulus."""
        print("-" * 80)
        slow_print(
            f"-> Introducing stimulus: '{style.BOLD}{stimulus.name}{style.RESET}'...", style_code=style.YELLOW)
        time.sleep(1)

        # 1. False-Structure Intolerance (FSI) Check
        # A powerful, protective veto against incoherent and imposed demands.
        # Powered by high 'volatility'.
        # A very low tolerance for incoherence
        fsi_threshold = (1.0 - self.profile["volatility"]) * 0.5
        if stimulus.is_imposed and stimulus.coherence < fsi_threshold:
            self._trigger_fsi(stimulus)
            return

        # 2. Ontologically Modulated Executive Function (OMEF) Check
        # The gate for engagement, which opens only for resonant tasks.
        # Governed by low 'industriousness' and high 'openness'.
        resonance_gap = abs(stimulus.coherence - self.ontological_focus)
        # High openness means a wider range of interest
        omef_threshold = (1.0 - self.profile["openness"]) * 2.0

        required_energy = stimulus.complexity * 5
        if self.energy < required_energy:
            wrap_print(
                "Engine energy levels are too low to engage with this stimulus.", style.YELLOW)
            self.state = "IDLE"
            return

        if resonance_gap < omef_threshold:
            self._trigger_omef(stimulus)
        else:
            wrap_print(
                f"Stimulus coherence ({stimulus.coherence:.2f}) does not align with current ontological focus ({self.ontological_focus:.2f}).", style.GREY)
            slow_print(
                "The engine remains indifferent. The stimulus is filtered out.", style_code=style.BLUE)
            self.state = "IDLE"

    def _trigger_fsi(self, stimulus: Stimulus):
        """Models the involuntary system shutdown of FSI."""
        self.state = "STALLED"
        self.state_timer = 0
        self.energy = max(0, self.energy - 40)  # FSI is energetically costly

        slow_print("\n!!! ONTOLOGICAL ALARM !!!", 0.03, style.RED + style.BOLD)
        wrap_print(
            f"Detected imposed structure '{stimulus.name}' with critically low coherence ({stimulus.coherence:.2f}).", style.RED)
        wrap_print("This is a violation of systemic integrity.", style.RED)
        time.sleep(0.5)
        slow_print("...Engaging somatic veto...", 0.05, style.RED)
        time.sleep(1)
        slow_print(
            "...Systemic seizure initiated. All cognitive processes halted.", 0.05, style.RED)
        slow_print(
            "...A smell of ozone and burnt wiring fills the chamber.", 0.05, style.RED)

    def _trigger_omef(self, stimulus: Stimulus):
        """Models the resonant activation and subsequent Meaning Storm."""
        self.state = "RESONATING"
        self.state_timer = 0
        self.energy -= stimulus.complexity * 5  # Engagement costs energy
        # Focus shifts slightly
        self.ontological_focus = (
            self.ontological_focus + stimulus.coherence) / 2

        slow_print("\n*** RESONANCE ACHIEVED ***",
                   0.03, style.GREEN + style.BOLD)
        wrap_print(
            f"Stimulus coherence ({stimulus.coherence:.2f}) aligns with ontological focus.", style.GREEN)
        wrap_print(
            "A phase change occurs. The engine's hum shifts from a low thrum to a high-frequency whine.", style.GREEN)
        time.sleep(1)
        self._meaning_storm(stimulus)

    def _meaning_storm(self, stimulus: Stimulus):
        """Simulates high-bandwidth parallel processing and ontological compression."""
        slow_print("\n>> INITIATING MEANING STORM <<", 0.04, style.CYAN)
        for i in range(5):
            print(
                f"{style.CYAN}    Synthesizing parallel data streams... {'.' * i}{style.RESET}", end="\r")
            time.sleep(random.uniform(0.3, 0.6))
        print("\n")

        slow_print(
            "Holistic gestalt insight achieved in a non-linear flash.", style_code=style.CYAN)
        slow_print(
            "Compressing high-dimensional complexity into a low-dimensional architecture...", style_code=style.CYAN)
        time.sleep(1)

        # Ontological Compression -> Blueprint Generation
        blueprint = self._generate_blueprint(stimulus)
        slow_print("\n--- ONTOLOGICAL BLUEPRINT GENERATED ---",
                   style_code=style.WHITE + style.BOLD)
        print(f"{style.BOLD}Source Stimulus:{style.RESET} {stimulus.name}")
        print(
            f"{style.BOLD}Core Principle:{style.RESET} {blueprint['principle']}")
        print(f"{style.BOLD}Key Vectors:{style.RESET}")
        for vector in blueprint['vectors']:
            print(f"  - {vector}")
        print(
            f"{style.BOLD}Structural Integrity:{style.RESET} {blueprint['integrity'] * 100:.1f}%")
        print("---------------------------------------")

    def _generate_blueprint(self, stimulus: Stimulus):
        """Creates a symbolic blueprint as the output of a meaning storm."""
        principles = ["Leverage Asymmetric Dependencies", "Establish Recursive Coherence", "Optimize for Emergent Simplicity",
                      "Invert the Primary Constraint", "Bridge Disparate Ontologies", "Minimize Entropic Drift"]
        vectors = ["Temporal Elasticity", "Structural Fidelity", "Resonance Gating",
                   "Epistemic Humility", "Anti-Narrative Filtering", "Somatic Attunement", "Symbolic Compression"]

        # Seed randomness for consistent output for the same stimulus
        random.seed(stimulus.name)
        blueprint = {
            "principle": random.choice(principles),
            "vectors": random.sample(vectors, k=min(len(vectors), stimulus.complexity)),
            "integrity": (stimulus.coherence + self.ontological_focus) / 2
        }
        return blueprint

    def tick(self):
        """
        Simulates the passage of time and the SCMF cycle.
        Called when the user chooses to 'Wait'.
        """
        self.state_timer += 1

        if self.state == "IDLE":
            # In IDLE state, energy slowly recovers and focus drifts.
            self.energy = min(100, self.energy + 1.5)
            self.ontological_focus = (
                self.ontological_focus + random.random()) / 2
            if self.energy < 30:
                return "The engine remains in a low-power state, emitting a barely audible hum."
            return "The engine idles. Internal systems cycle slowly. Ontological focus drifts..."

        elif self.state == "RESONATING":
            # Resonance is powerful but unsustainable.
            self.energy = max(0, self.energy - 3)
            if self.energy <= 0 or self.state_timer > 5:
                self.state = "IDLE"
                self.state_timer = 0
                return f"{style.YELLOW}The resonant frequency fades. The engine spools down, returning to an idle state to cool and recover.{style.RESET}"
            return "The engine continues to operate at peak capacity, processing the resonant stimulus."

        elif self.state == "STALLED":
            # Recovery from FSI shutdown is slow and requires time.
            self.energy = min(100, self.energy + 0.5)  # Very slow recovery
            if self.state_timer > 6:
                self.state = "IDLE"
                self.state_timer = 0
                return f"{style.YELLOW}System diagnostics complete. The ontological violation has been purged. The engine slowly re-initializes to an idle state.{style.RESET}"
            return "The engine is stalled. Warning lights flash. A system-wide diagnostic and reboot is in progress."
        return ""

    def ask_the_mirror(self):
        """
        Embodies the 'AI as Epistemic Mirror' concept.
        Provides a meta-reflection on the engine's own state and principles.
        """
        print("-" * 80)
        slow_print("-> Querying the Epistemic Mirror...",
                   style_code=style.MAGENTA)
        time.sleep(1)
        wrap_print("The Mirror reflects the internal state of the Chamber, articulating patterns without judgment...",
                   style_code=style.MAGENTA + style.ITALIC)

        if self.state == "IDLE":
            wrap_print(
                f"\nReflection: The system is in an incubatory phase. Energy is being conserved while it awaits a resonant signal. This is not inactivity, but a state of potential. The current ontological focus ({self.ontological_focus:.2f}) suggests an attunement towards patterns of abstract structure.", style_code=style.MAGENTA)
        elif self.state == "RESONATING":
            wrap_print(f"\nReflection: The system is in a state of high cognitive flow, a 'meaning storm'. The gate of OMEF has been unlocked. Energy is being expended rapidly to compress complexity into a coherent blueprint. This state is productive but energetically expensive and temporary.", style_code=style.MAGENTA)
        elif self.state == "STALLED":
            wrap_print(f"\nReflection: The system's protective mechanism, FSI, has been triggered. An imposed, incoherent structure was rejected to preserve ontological integrity. This shutdown is a non-volitional, adaptive defense, not a malfunction. Recovery requires time and a safe, coherent environment.", style_code=style.MAGENTA)


# --- Main Application Loop ---

def main():
    """The main function to run the interactive simulation."""
    engine = ResonanceEngine()

    print("=" * 80)
    slow_print("Resonance Chamber v2.5 Initializing...", 0.03, style.BOLD)
    slow_print("Cognitive-Ontological Framework: LOADED")
    print(
        f"Engine Profile -> Industriousness: {engine.profile['industriousness']} | Volatility: {engine.profile['volatility']} | Openness: {engine.profile['openness']}")
    print("=" * 80)

    while True:
        print("\n" + "=" * 80)
        print(f"ENGINE STATUS: {engine._get_status_display()}")
        print("-" * 80)

        prompt = f"Choose an action: [{style.YELLOW}I{style.RESET}]ntroduce Stimulus, [{style.BLUE}W{style.RESET}]ait, [{style.MAGENTA}A{style.RESET}]sk the Mirror, [{style.GREY}Q{style.RESET}]uit"
        action = input(f"{prompt}\n> ").upper()

        if action == "Q":
            slow_print("...Powering down the Resonance Chamber.",
                       style_code=style.GREY)
            break

        elif action == "I":
            try:
                stimulus_name = input(
                    "  Enter stimulus name (e.g., 'Client Email', 'A fleeting idea'): ")
                coherence_in = int(
                    input("  Enter coherence [0-100] (0=nonsense, 100=perfectly meaningful): "))
                complexity_in = int(input("  Enter complexity [1-10]: "))
                imposed_in = input(
                    "  Is this an imposed demand? [y/n]: ").upper()

                stimulus = Stimulus(
                    name=stimulus_name,
                    coherence=coherence_in / 100.0,
                    complexity=complexity_in,
                    is_imposed=(imposed_in == "Y")
                )
                engine.introduce_stimulus(stimulus)

            except ValueError:
                print(
                    f"{style.RED}Invalid input. Please enter numbers for coherence and complexity.{style.RESET}")

        elif action == "W":
            slow_print("...Time passes...", style_code=style.BLUE)
            time.sleep(1)
            status_update = engine.tick()
            wrap_print(status_update, style_code=style.BLUE)

        elif action == "A":
            engine.ask_the_mirror()

        else:
            print(f"{style.RED}Unknown command.{style.RESET}")


if __name__ == "__main__":
    main()
