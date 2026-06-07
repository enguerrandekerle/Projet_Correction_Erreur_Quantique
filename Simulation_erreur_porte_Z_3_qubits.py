from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np
import matplotlib.pyplot as plt

sim = AerSimulator()
P_VALUES = np.linspace(0, 0.5, 11)
N_SHOTS = 500

# ============================================================================
# SIMULATION ERREUR Z (phase-flip)
# Code a 3 qubits phase-flip :
#   encodage : 2 CNOT + H sur chaque qubit -> base {|+>, |->}
#   erreur Z dans cette base = erreur X apres H
#   syndrome dans la base Hadamard
# ============================================================================

def syndrome_block_Z(qc):
    """Syndrome dans la base Hadamard : H puis syndrome X puis H"""
    qc.h(0); qc.h(1); qc.h(2)
    qc.cx(0, 3)
    qc.cx(1, 3)  # ancilla 3 = q0 XOR q1 (dans base Hadamard)
    qc.cx(0, 4)
    qc.cx(2, 4)  # ancilla 4 = q0 XOR q2 (dans base Hadamard)
    qc.h(0); qc.h(1); qc.h(2)

def appliquer_correction_Z(qc, syndrome):
    """Correction : porte Z sur le qubit identifie."""
    match syndrome:
        case '01': qc.z(0)
        case '10': qc.z(1)
        case '11': qc.z(2)

def simuler_un_tir_Z(p):
    # ── Circuit 1 : encodage phase-flip + erreur Z + syndrome ─
    qc1 = QuantumCircuit(5, 2)

    # Encodage phase-flip : 2 CNOT + H^3
    qc1.h(0)
    qc1.cx(0, 1)
    qc1.cx(0, 2)
    qc1.h(0); qc1.h(1); qc1.h(2)

    # Erreur Z
    qubit_erreur = None
    if np.random.rand() < p:
        qubit_erreur = int(np.random.rand() * 3)
        qc1.z(qubit_erreur)

    # Syndrome dans la base Hadamard
    syndrome_block_Z(qc1)
    qc1.measure(3, 1)
    qc1.measure(4, 0)

    result1 = sim.run(qc1, shots=1).result()
    s = list(result1.get_counts().keys())[0][-2:]

    # ── Circuit 2 : meme etat + meme erreur + correction Z ────
    qc2 = QuantumCircuit(5, 2)

    qc2.h(0)
    qc2.cx(0, 1)
    qc2.cx(0, 2)
    qc2.h(0); qc2.h(1); qc2.h(2)

    if qubit_erreur is not None:
        qc2.z(qubit_erreur)

    appliquer_correction_Z(qc2, s)

    syndrome_block_Z(qc2)
    qc2.measure(3, 1)
    qc2.measure(4, 0)

    result2 = sim.run(qc2, shots=1).result()
    s2 = list(result2.get_counts().keys())[0][-2:]

    return s, (s2 == '00')

def simuler_p_Z(p, n_shots):
    freq = {'00': 0, '01': 0, '10': 0, '11': 0}
    succes = 0
    for _ in range(n_shots):
        syndrome, ok = simuler_un_tir_Z(p)
        freq[syndrome] += 1
        if ok:
            succes += 1
    for k in freq:
        freq[k] /= n_shots
    return freq, succes / n_shots

# ── Simulation ────────────────────────────────────────────────
resultats = {'p': [], 'f00': [], 'f01': [], 'f10': [], 'f11': [], 'succes': []}

for p in P_VALUES:
    print(f"Z - p = {p:.2f}...")
    freq, suc = simuler_p_Z(p, N_SHOTS)
    resultats['p'].append(p)
    resultats['f00'].append(freq['00'])
    resultats['f01'].append(freq['01'])
    resultats['f10'].append(freq['10'])
    resultats['f11'].append(freq['11'])
    resultats['succes'].append(suc)

p_array = np.array(P_VALUES)
theo_p3 = p_array**2 * (3 - 2*p_array)

# ── Graphique 4a : frequence des syndromes ────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(resultats['p'], resultats['f00'], 'o-',
        label='Syndrome 00 (aucune erreur)', color='black')
ax.plot(resultats['p'], resultats['f01'], 's-',
        label='Syndrome 01 (erreur q0)', color='blue')
ax.plot(resultats['p'], resultats['f10'], '^-',
        label='Syndrome 10 (erreur q1)', color='green')
ax.plot(resultats['p'], resultats['f11'], 'D-',
        label='Syndrome 11 (erreur q2)', color='red')
ax.plot(p_array, 1 - p_array, 'k--', linewidth=2,
        label='Theorique 1-p')
ax.plot(p_array, p_array / 3, 'b--', linewidth=2,
        label='Theorique p/3')
ax.set_xlabel("Probabilite d'erreur p")
ax.set_ylabel("Frequence du syndrome")
ax.set_title("Erreur Z : frequence des syndromes en fonction de p")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graph_4a.png", dpi=150, bbox_inches='tight')
plt.show()

# ── Graphique 4b : taux de succes ─────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(resultats['p'], resultats['succes'], 's-',
        label='Simulation', color='red', linewidth=2)
ax.plot(p_array, 1 - theo_p3, 'k--', linewidth=2,
        label='Theorique 1 - p^2(3-2p)')
ax.set_xlabel("Probabilite d'erreur p")
ax.set_ylabel("Taux de succes")
ax.set_title("Erreur Z : taux de succes de la correction")
ax.set_ylim([0, 1.05])
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graph_4b.png", dpi=150, bbox_inches='tight')
plt.show()

print("Simulation Z terminee !")
