import random
import math
import time

from common import run, neighborhood, Result


class Algorithm:
	"""
	Abstract class for local search algorithm
	"""

	name = ""
	full_name = ""

	def __init__(self, n1, n2, n3, S0, k_max):
		self.n1 = n1
		self.n2 = n2
		self.n3 = n3
		self.S0 = S0
		self.k_max = k_max

		self.params = {
			"method": self.name,
			"n1": self.n1,
			"n2": self.n2,
			"n3": self.n3,
			"S0": self.S0,
			"n_iter": self.k_max,
		}

	def print_params(self):
		print(self.full_name)
		print(self.params)

	def cost(self, S):
		return run(S, self.n1, self.n2, self.n3)

	def optimize(self):
		raise NotImplementedError

	def save(self):
		res = Result()
		print("Executed in", self.runtime, "s")
		print("Best solution:", self.S_best, "with", self.E_best, "MPoints/s")
		res.set_data(self.params, self.S_list, self.E_list, self.S_best, self.E_best, self.runtime)
		res.save()


class Greedy(Algorithm):

	name = "ghc"
	full_name = "Greedy Hill Climbing"

	def __init__(self, n1, n2, n3, S0, k_max):
		super().__init__(n1, n2, n3, S0, k_max)

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best = self.cost(S_best)
		L_neigh = neighborhood(S_best, self.n1, self.n2, self.n3)

		S_list = [S_best]
		E_list = [E_best]

		k = 0
		NewBetterS = True
		while(k < self.k_max and NewBetterS):
			S = L_neigh.pop()
			E = self.cost(S)
			for S_prime in L_neigh:
				E_prime = self.cost(S_prime)
				if E_prime > E:
					S = S_prime
					E = E_prime
			if E > E_best:
				S_best = S
				E_best = E
				L_neigh = neighborhood(S_best, self.n1, self.n2, self.n3)
			else:
				NewBetterS = False
			k = k + 1
			print('k: ', k)
			S_list.append(S)
			E_list.append(E)
		
		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0


class SimulatedAnnealing(Algorithm):

	name = "sa"
	full_name = "Simulated Annealing"

	def __init__(self, n1, n2, n3, S0, k_max, T0, temp_decay):
		super().__init__(n1, n2, n3, S0, k_max)

		self.T0 = T0
		self.params["T0"] = T0

		self.params["temp_decay"] = temp_decay
		if temp_decay == "linear":
			self.temp_decay = self.decay_linear
		elif temp_decay == "geometric":
			self.temp_decay = self.decay_geometric
		else:
			raise ValueError("Invalid temp_decay")

	def decay_geometric(self, k):
		a = 10**(math.log10(0.01)/self.k_max)
		return (a**k)*self.T0

	def decay_linear(self, k):
		return self.T0*(1 - k/self.k_max)

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best = self.cost(self.S0)
		S = self.S0
		E = E_best
		neighbors = neighborhood(self.S0, self.n1, self.n2, self.n3)
		T = self.T0
		
		S_list = [S_best]
		E_list = [E_best]

		for k in range(self.k_max):
			S_new = random.choice(neighbors)
			E_new = self.cost(S_new)
			print(f"[{k}/{self.k_max}] {S_new} {E_new}", end='')
			if E_new > E or random.random() < math.exp(-(E-E_new)/T):
				S = S_new
				E = E_new
				neighbors = neighborhood(S, self.n1, self.n2, self.n3)
				if E > E_best:
					S_best = S
					E_best = E
				print(" ACCEPTED")
			else:
				print(" REJECTED")
			T = self.temp_decay(k)
			
			S_list.append(S)
			E_list.append(E)
		
		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0


class TabuSA(SimulatedAnnealing):

	name = "tabu_sa"
	full_name = "Tabu Simulated Annealing"

	def __init__(self, n1, n2, n3, S0, k_max, T0, temp_decay, tabu_size):
		super().__init__(n1, n2, n3, S0, k_max, T0, temp_decay)
		
		self.tabu_size = tabu_size
		self.params["tabu_size"] = tabu_size

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best = self.cost(self.S0)
		S = self.S0
		E = E_best
		neighbors = neighborhood(self.S0, self.n1, self.n2, self.n3)
		T = self.T0

		Ltabu = [S_best]

		S_list = [S_best]
		E_list = [E_best]

		for k in range(self.k_max):
			S_new = random.choice(neighbors)
			while S_new in Ltabu:
				S_new = random.choice(neighbors)
			E_new = self.cost(S_new)
			print(f"[{k}/{self.k_max}] {S_new} {E_new}", end='')
			if E_new > E or random.random() < math.exp(-(E-E_new)/T):
				S = S_new
				E = E_new
				neighbors = neighborhood(S, self.n1, self.n2, self.n3)
				if E > E_best:
					S_best = S
					E_best = E
				Ltabu = self.fifo_add(S_best, Ltabu)
				print(" ACCEPTED")
			else:
				print(" REJECTED")
			print(Ltabu)
			T = self.temp_decay(k)

			S_list.append(S)
			E_list.append(E)

		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0

	def fifo_add(self, S_best, Ltabu):
		if len(Ltabu) == self.tabu_size:
			Ltabu.pop(0)
		Ltabu.append(S_best)
		return Ltabu


class TunnelingSA(SimulatedAnnealing):

	name = "tunnel_sa"
	full_name = "Tunneling Simulated Annealing"

	def __init__(self, n1, n2, n3, S0, k_max, T0, temp_decay, cost_fun, E_tunnel):
		super().__init__(n1, n2, n3, S0, k_max, T0, temp_decay)
		
		self.params["cost_fun"] = cost_fun
		if cost_fun == "average":
			self.cost = self.cost_average
		elif cost_fun == "stochastic":
			self.cost = self.cost_stochastic
		else:
			raise ValueError("Invalid cost_fun")

		self.params["E_tunnel"] = E_tunnel
		self.E_tunnel = E_tunnel

	def cost_average(self, S):
		E = run(S, self.n1, self.n2, self.n3)
		if E < self.E_tunnel:
			return (E + self.E_tunnel)/2, E
		else:
			return E, E

	def cost_stochastic(self, S):
		gamma = 0.004
		E = run(S, self.n1, self.n2, self.n3)
		return math.exp(-gamma*(self.E_tunnel - E)) - 1, E

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best_tun, E_best = self.cost(self.S0)
		S = self.S0
		E_tun = E_best_tun
		E = E_best
		neighbors = neighborhood(self.S0, self.n1, self.n2, self.n3)
		T = self.T0

		S_list = [S_best]
		E_list = [E_best]

		for k in range(self.k_max):
			S_new = random.choice(neighbors)
			E_new_tun, E_new  = self.cost(S_new)
			print(f"[{k}/{self.k_max}] {S_new} {E_new}", end='')
			if E_new_tun > E_tun or random.random() < math.exp(-(E_tun-E_new_tun)/T):
				S = S_new
				E_tun = E_new_tun
				E = E_new
				neighbors = neighborhood(S, self.n1, self.n2, self.n3)
				if E_tun > E_best_tun:
					S_best = S
					E_best_tun = E_tun
					E_best = E
				print(" ACCEPTED")
			else:
				print(" REJECTED")
			T = self.temp_decay(k)
			
			S_list.append(S)
			E_list.append(E)

		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0


class LAHC(Algorithm):

	name = "lahc"
	full_name = "Late Acceptance Hill Climbing"

	def __init__(self, n1, n2, n3, S0, k_max, Lh):
		super().__init__(n1, n2, n3, S0, k_max)

		self.Lh = Lh
		self.params["Lh"] = Lh

	def optimize(self):
		time0 = time.time()
		self.print_params()

		S_best = self.S0
		E_best = self.cost(self.S0)
		S = S_best
		E = E_best
		neighbors = neighborhood(S, self.n1, self.n2, self.n3)
		fitness = [E_best] * self.Lh # history of previous costs

		S_list = [S_best]
		E_list = [E_best]

		k_idle = 0
		for k in range(self.k_max):
			S_new = random.choice(neighbors)
			E_new = self.cost(S_new)
			print(f"[{k}/{self.k_max}] {S_new} {E_new}", end='')
			
			if E_new <= E:
				k_idle += 1
			else:
				k_idle = 0

			v = k % self.Lh
			if E_new > fitness[v] or E_new >= E:
				S = S_new
				E = E_new
				neighbors = neighborhood(S, self.n1, self.n2, self.n3)
				print(" ACCEPTED")
				if E >= E_best:
					S_best = S
					E_best = E
			else:
				print(" REJECTED")

			if E > fitness[v]:
				fitness[v] = E

			S_list.append(S)
			E_list.append(E)
		
		self.S_best = S_best
		self.E_best = E_best
		self.S_list = S_list
		self.E_list = E_list
		self.runtime = time.time() - time0

