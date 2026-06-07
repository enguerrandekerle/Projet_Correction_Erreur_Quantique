import numpy as np
import random as rd
import matplotlib.pyplot as plt

# ============================================================
# Paramètres généraux
# ============================================================

SEED = 12345
rd.seed(SEED)
np.random.seed(SEED)

N_SHOTS_GRAPH2 = 4096
N_SHOTS_GRAPH3 = 1000
P_VALUES_GRAPH2 = np.linspace(0, 0.5, 11)
P_VALUES_GRAPH3 = np.linspace(0, 0.5, 11)

# ============================================================
# graph_2.png
# Simulation d'une erreur de porte X
# Théorie : P(0)=p et P(1)=1-p
# Simulation : |0> -- X -- erreur X avec proba p -- mesure
# ============================================================

theory_p0 = []
theory_p1 = []
sim_p0 = []
sim_p1 = []

for p in P_VALUES_GRAPH2:
    count_0 = 0
    count_1 = 0

    for _ in range(N_SHOTS_GRAPH2):
        bit = 0

        # Porte X idéale : |0> -> |1>
        bit = 1 - bit

        # Erreur X supplémentaire avec probabilité p
        if rd.random() < p:
            bit = 1 - bit

        if bit == 0:
            count_0 += 1
        else:
            count_1 += 1

    theory_p0.append(p)
    theory_p1.append(1 - p)
    sim_p0.append(count_0 / N_SHOTS_GRAPH2)
    sim_p1.append(count_1 / N_SHOTS_GRAPH2)

plt.figure(figsize=(8, 5))
plt.plot(P_VALUES_GRAPH2, theory_p0, marker="o", label="Théorie P(0)=p")
plt.plot(P_VALUES_GRAPH2, sim_p0, marker="x", linestyle="--", label="Simulation P(0)")
plt.plot(P_VALUES_GRAPH2, theory_p1, marker="o", label="Théorie P(1)=1-p")
plt.plot(P_VALUES_GRAPH2, sim_p1, marker="x", linestyle="--", label="Simulation P(1)")
plt.xlabel("Probabilité d'erreur p")
plt.ylabel("Probabilité mesurée")
plt.title("Simulation d'une erreur de porte X")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("graph_2.png", dpi=300)
plt.show()

# ============================================================
# graph_3a.png
# Fréquence des syndromes du code 3 qubits
#
# Convention :
# 00 : aucune erreur
# 01 : erreur sur le qubit 1
# 10 : erreur sur le qubit 2
# 11 : erreur sur le qubit 0
#
# Modèle : avec probabilité p, UNE erreur X arrive
# sur l'un des trois qubits, choisi au hasard.
# ============================================================

freq = {"00": [], "01": [], "10": [], "11": []}

mapping_erreur_syndrome = {
    None: "00",
    0: "11",
    1: "01",
    2: "10",
}

for p in P_VALUES_GRAPH3:
    resultats = {"00": 0, "01": 0, "10": 0, "11": 0}

    for _ in range(N_SHOTS_GRAPH3):
        qubit_erreur = None

        if rd.random() < p:
            qubit_erreur = rd.randint(0, 2)

        syndrome = mapping_erreur_syndrome[qubit_erreur]
        resultats[syndrome] += 1

    for s in freq:
        freq[s].append(resultats[s] / N_SHOTS_GRAPH3)

theory_00 = 1 - P_VALUES_GRAPH3
theory_error = P_VALUES_GRAPH3 / 3

plt.figure(figsize=(8, 5))
plt.plot(P_VALUES_GRAPH3, freq["00"], marker="o", label="00 : aucune erreur")
plt.plot(P_VALUES_GRAPH3, freq["01"], marker="s", label="01 : erreur qubit 1")
plt.plot(P_VALUES_GRAPH3, freq["10"], marker="^", label="10 : erreur qubit 2")
plt.plot(P_VALUES_GRAPH3, freq["11"], marker="D", label="11 : erreur qubit 0")
plt.plot(P_VALUES_GRAPH3, theory_00, linestyle="--", label="Théorie 00 : 1-p")
plt.plot(P_VALUES_GRAPH3, theory_error, linestyle="--", label="Théorie erreurs : p/3")
plt.xlabel("Probabilité d'erreur p")
plt.ylabel("Fréquence des syndromes")
plt.title("Fréquence des syndromes du code 3 qubits")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("graph_3a.png", dpi=300)
plt.show()

# ============================================================
# graph_3b.png
# Taux de succès de la correction 3 qubits
#
# Dans ce modèle, il y a au maximum UNE erreur X.
# Le code 3 qubits peut donc toujours la corriger.
# ============================================================

taux_succes = []

for p in P_VALUES_GRAPH3:
    succes = 0

    for _ in range(N_SHOTS_GRAPH3):
        qubit_erreur = None

        if rd.random() < p:
            qubit_erreur = rd.randint(0, 2)

        syndrome = mapping_erreur_syndrome[qubit_erreur]

        if syndrome == "00":
            qubit_corrige = None
        elif syndrome == "11":
            qubit_corrige = 0
        elif syndrome == "01":
            qubit_corrige = 1
        elif syndrome == "10":
            qubit_corrige = 2

        if qubit_corrige == qubit_erreur:
            succes += 1

    taux_succes.append(succes / N_SHOTS_GRAPH3)

plt.figure(figsize=(8, 5))
plt.plot(P_VALUES_GRAPH3, taux_succes, marker="o", label="Simulation")
plt.axhline(y=1, linestyle="--", label="Théorie : succès parfait")
plt.xlabel("Probabilité d'erreur p")
plt.ylabel("Taux de succès")
plt.title("Taux de succès de la correction 3 qubits")
plt.ylim(0.95, 1.01)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("graph_3b.png", dpi=300)
plt.show()