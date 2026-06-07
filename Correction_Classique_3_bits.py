import numpy as np 
import random as rd

q0 = np.array([1,0])
q1 = np.array([0,1])


q = (1/(2**0.5))*(q0+q1)

print (q)

alph = q[0]
bet = q[1]

p0 = abs(q[0]) **2
p1 = abs(q[1]) **2

#porte HADAMARD

H = (1/2**0.5) * np.array([
    [1, 1],
    [1, -1]])

test = q1 @ H

print(test)
 
#Portes Pauli

X = np.array([
    [0,1],
    [1,0]
])

test2 = q0 @ X
print(test2)

Z = np.array([
    [1,0],
    [0,-1]
])

def bit_flip_erreur(q,p_bit):
    U = rd.random()
    if U < p_bit :
        return X @ q 
    return q 

def phase_erreur(q,p_phase):
    U = rd.random()
    if U < p_phase :
        return Z @ q 
    return q 


def encoder3bits(q):
    q3 = []
    for i in range(3):
        q3.append(q)
    return q3

def bit_flip(q, p):
    q3 = encoder3bits(q)
    for i in range(len(q3)):
        if rd.random() < p:
            q3[i] = 1 - q3[i]
    return q3

def corriger(q3):
    # vote majoritaire
    S = 0
    for i in range(len(q3)):
        S += q3[i]
    if S >= 2 :
            return 1
    else:
        return 0
    

def simulation(p, Nmc):
    erreurs_sans_correction = 0
    erreurs_avec_correction = 0

    for _ in range(Nmc):
        bit_initial = rd.randint(0, 1)

        # Sans correction

        bit_bruite =  bit_flip(bit_initial, p)[0]

        if bit_bruite != bit_initial:
            erreurs_sans_correction += 1

        # Avec correction

        code_bruite = bit_flip(bit_initial, p)
        bit_corrige = corriger(code_bruite)

        if bit_corrige != bit_initial:
            erreurs_avec_correction += 1

    return erreurs_sans_correction / Nmc, erreurs_avec_correction / Nmc


sans, avec = simulation(p=0.1, Nmc=10000)

print("Taux d'erreur sans correction :", sans)
print("Taux d'erreur avec correction :", avec)



