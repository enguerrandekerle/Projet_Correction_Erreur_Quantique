from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np
import matplotlib.pyplot as plt

sim = AerSimulator()
P_VALUES = np.linspace(0, 0.5, 11)
N_SHOTS = 500

# ============================================================================
# SIMULATION ERREUR X (bit-flip)
# Code a 3 qubits : encodage -> erreur X -> syndrome -> correction
# Syndrome : a1 = q0 XOR q1, a2 = q0 XOR q2
#   00 -> aucune erreur
#   01 -> erreur sur q0
#   10 -> erreur sur q1
#   11 -> erreur sur q2
# ============================================================================

def syndrome_block_X(qc):
    qc.cx(0, 3)
    qc.cx(1, 3)  # ancilla 3 = q0 XOR q1
    qc.cx(0, 4)
    qc.cx(2, 4)  # ancilla 4 = q0 XOR q2

def appliquer_correction(qc, syndrome):
    match syndrome:
        case '01': qc.x(0)
        case '10': qc.x(1)
        case '11': qc.x(2)

def simuler_un_tir_X(p):
    # ── Circuit 1 : encodage + erreur + mesure syndrome ───────
    qc1 = QuantumCircuit(5, 2)
    qc1.h(0)
    qc1.cx(0, 1)
    qc1.cx(0, 2)

    qubit_erreur = None
    if np.random.rand() < p:
        qubit_erreur = int(np.random.rand() * 3)
        qc1.x(qubit_erreur)

    syndrome_block_X(qc1)
    qc1.measure(3, 1)  # q0 XOR q1 -> bit 1
    qc1.measure(4, 0)  # q0 XOR q2 -> bit 0

    result1 = sim.run(qc1, shots=1).result()
    s = list(result1.get_counts().keys())[0][-2:]

    # ── Circuit 2 : meme etat + meme erreur + correction ──────
    qc2 = QuantumCircuit(5, 2)
    qc2.h(0)
    qc2.cx(0, 1)
    qc2.cx(0, 2)

    if qubit_erreur is not None:
        qc2.x(qubit_erreur)

    appliquer_correction(qc2, s)

    syndrome_block_X(qc2)
    qc2.measure(3, 1)
    qc2.measure(4, 0)

    result2 = sim.run(qc2, shots=1).result()
    s2 = list(result2.get_counts().keys())[0][-2:]

    return s, (s2 == '00')

def simuler_p_X(p, n_shots):
    freq = {'00': 0, '01': 0, '10': 0, '11': 0}
    succes = 0
    for _ in range(n_shots):
        syndrome, ok = simuler_un_tir_X(p)
        freq[syndrome] += 1
        if ok:
            succes += 1
    for k in freq:
        freq[k] /= n_shots
    return freq, succes / n_shots

# ── Simulation ────────────────────────────────────────────────
resultats = {'p': [], 'f00': [], 'f01': [], 'f10': [], 'f11': [], 'succes': []}

for p in P_VALUES:
    print(f"X - p = {p:.2f}...")
    freq, suc = simuler_p_X(p, N_SHOTS)
    resultats['p'].append(p)
    resultats['f00'].append(freq['00'])
    resultats['f01'].append(freq['01'])
    resultats['f10'].append(freq['10'])
    resultats['f11'].append(freq['11'])
    resultats['succes'].append(suc)

p_array = np.array(P_VALUES)
theo_p3 = p_array**2 * (3 - 2*p_array)

# ── Graphique 3a : frequence des syndromes ────────────────────
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
        label='Theorique 1-p (pas d erreur)')
ax.plot(p_array, p_array / 3, 'b--', linewidth=2,
        label='Theorique p/3 (erreur sur 1 qubit)')
ax.set_xlabel("Probabilite d'erreur p")
ax.set_ylabel("Frequence du syndrome")
ax.set_title("Erreur X : frequence des syndromes en fonction de p")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graph_3a.png", dpi=150, bbox_inches='tight')
plt.show()

# ── Graphique 3b : taux de succes ─────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(resultats['p'], resultats['succes'], 'o-',
        label='Simulation', color='blue', linewidth=2)
ax.plot(p_array, 1 - theo_p3, 'k--', linewidth=2,
        label='Theorique 1 - p^2(3-2p)')
ax.set_xlabel("Probabilite d'erreur p")
ax.set_ylabel("Taux de succes")
ax.set_title("Erreur X : taux de succes de la correction")
ax.set_ylim([0, 1.05])
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graph_3b.png", dpi=150, bbox_inches='tight')
plt.show()

print("Simulation X terminee !")
