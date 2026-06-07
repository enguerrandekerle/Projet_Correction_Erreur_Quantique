from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Simulation d'une erreur de porte X sur 1 qubit
# Objectif : montrer le bruitage de la porte X
# ============================================================

SHOTS = 4096
P_VALUES = np.linspace(0, 0.5, 11)
SEED = 12345


def build_bit_flip_noise_model(p):
    """
    Modèle de bruit :
    après chaque porte X, une erreur X supplémentaire
    est appliquée avec une probabilité p.
    """
    error_x = pauli_error([
        ("I", 1 - p),
        ("X", p)
    ])

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(error_x, ["x"])

    return noise_model


def x_gate_circuit():
    """
    Circuit testé :
    |0> -- X -- mesure
    """
    qc = QuantumCircuit(1, 1)

    qc.x(0)
    qc.measure(0, 0)

    return qc


def run_simulation(p):
    """
    Exécute le circuit avec le modèle de bruit.
    """
    noise_model = build_bit_flip_noise_model(p)
    simulator = AerSimulator(
        noise_model=noise_model,
        seed_simulator=SEED
    )

    qc = x_gate_circuit()
    tqc = transpile(qc, simulator)

    result = simulator.run(tqc, shots=SHOTS).result()
    counts = result.get_counts()

    return counts


def frequency(counts, bit):
    """
    Calcule la fréquence d'un résultat de mesure.
    """
    return counts.get(bit, 0) / SHOTS


# ============================================================
# Simulation pour plusieurs valeurs de p
# ============================================================

theory_p0 = []
theory_p1 = []
simulation_p0 = []
simulation_p1 = []

for p in P_VALUES:
    counts = run_simulation(float(p))

    theory_p0.append(p)
    theory_p1.append(1 - p)

    simulation_p0.append(frequency(counts, "0"))
    simulation_p1.append(frequency(counts, "1"))


# ============================================================
# Graphe : théorie contre simulation
# ============================================================

plt.figure(figsize=(8, 5))

plt.plot(P_VALUES, theory_p1, marker="o",
         label="Théorie P(1)=1-p")
plt.plot(P_VALUES, simulation_p1, marker="x", linestyle="--",
         label="Simulation Qiskit P(1)")

plt.plot(P_VALUES, theory_p0, marker="o",
         label="Théorie P(0)=p")
plt.plot(P_VALUES, simulation_p0, marker="x", linestyle="--",
         label="Simulation Qiskit P(0)")

plt.xlabel("Probabilité d'erreur p")
plt.ylabel("Probabilité mesurée")
plt.title("Bruit de type X après une porte X")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig("graph_2.png", dpi=300)
plt.show()