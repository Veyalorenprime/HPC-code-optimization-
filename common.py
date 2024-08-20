import subprocess
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Constants
ISO3DFD_DIR = os.path.expanduser("~") + "/iso3dfd-st7"
RESULTS_DIR = os.path.join(os.getcwd(), "results")

def get_algo_by_name(name):
	algo_dict = {
		"ghc": "Greedy Hill Climbing",
		"sa": "Simulated Annealing",
		"tabu_sa": "Tabu SA",
		"tunnel_sa": "Tunneling SA",
		"lahc": "Late Acceptance Hill Climbing"
	}
	return algo_dict[name]

class Result:
	"""
	Class for interfacing with optimization results, enabling loading, saving and plotting.
	
	Each instantiation corresponds to an optimization run.
	History of attempted solutions are saved in a numbered .csv file, and parameters and metadata
	are saved in a common summary.json file
	"""
	def __init__(self, id=None):
		self.id = None
		self.json_fn = os.path.join(RESULTS_DIR, "summary.json")
		if id != None:
			self.load_from_id(id)

	def load_from_id(self, id):
		self.id = id
		with open(self.json_fn, "r") as f:
			summary = json.load(f)
		id_str = str(id)
		self.params = summary[id_str]["params"]
		self.S_best = summary[id_str]["S_best"]
		self.E_best = summary[id_str]["E_best"]
		self.runtime = summary[id_str]["runtime"]

		csv_fn = os.path.join(RESULTS_DIR, f"{self.id:05d}.csv")
		self.data = pd.read_csv(csv_fn, index_col=0)

	def set_data(self, params, S_list, E_list, S_best, E_best, runtime):
		self.data = pd.DataFrame(S_list, columns = ["Olevel", "simd", "NbTh", "n1_thrd_block", "n2_thrd_block", "n3_thrd_block"])
		self.data["E"] = E_list
		self.params = params
		self.S_best = S_best
		self.E_best = E_best
		self.runtime = runtime

	def calculate_id(self):
			i = -1
			for name in os.listdir(RESULTS_DIR):
					if name[-4:] == ".csv":
						i = max(i, int(name[:-4]))
			self.id = i+1

	def save(self):
			if not os.path.exists(RESULTS_DIR):
				subprocess.run(f"mkdir -p {RESULTS_DIR}", shell=True, stdout=subprocess.PIPE)
			if self.id == None:
					self.calculate_id()
			if os.path.exists(self.json_fn):
					with open(self.json_fn, "r") as f:
							summary = json.load(f)
			else:
					summary = {}
			id_str = str(self.id)
			summary[id_str] = {}
			summary[id_str]["params"] = self.params
			summary[id_str]["S_best"] = self.S_best
			summary[id_str]["E_best"] = self.E_best
			summary[id_str]["runtime"] = self.runtime
			print("Saving summary file to", self.json_fn)
			with open(self.json_fn, "w") as f:
					json.dump(summary, f, indent=4)

			csv_fn = os.path.join(RESULTS_DIR, f"{self.id:05d}.csv")
			print("Saving result file to", csv_fn)
			self.data.to_csv(csv_fn)

	def print_summary(self):
		print(f"=== Result for trial {self.id:05d} ===")
		print("Parameters:")
		for key in self.params:
			print(f"\t{key}\t{self.params[key]}")
		print(f"Executed in {self.runtime:.2f} s")
		print(f"Best result: {self.E_best} MPoints/s with {self.S_best}")
		print()
		print(self.data)

	def plot(self, title, label):
		if label == None:
			label = f"{self.id:05d}"
		if title == None:
			title = get_algo_by_name(self.params["method"])
		# plt.rcParams.update({'font.size': 22})
		plt.plot(self.data["E"], label=label)
		plt.title(title)
		plt.xlabel("Iteration")
		plt.ylabel("Throughput (MPoints/s)")
		plt.legend()
		plt.grid(True)


def make(Olevel, simd):
	"""
	Compiles the iso3dfd code
	"""
	filename = f"iso3dfd_dev13_cpu_{simd}_{Olevel}.exe"
	if not os.path.exists("./bin/" + filename):
		# Make command
		cmd = f"make Olevel=-{Olevel} simd={simd} last"
		print("Running command:", cmd)
		res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, cwd=ISO3DFD_DIR)

		# Copy the executable
		cmd = f"mkdir -p bin && cp {ISO3DFD_DIR}/bin/iso3dfd_dev13_cpu_{simd}.exe ./bin/{filename}"
		print("Runing command:", cmd)
		res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
	return filename

def run_iso3dfd(n1, n2, n3, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block, filename):
	cmd = f"KMP_AFFINITY=balanced,granularity=core ./bin/{filename} {n1} {n2} {n3} {NbTh} 100 {n1_thrd_block} {n2_thrd_block} {n3_thrd_block} > output.txt"
	res = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE)

def run_energy(n1, n2, n3, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block, filename):
	# log into John3 machine from Chome with "su -" command.
	cmd = f"/opt/cpu_monitor/cpu_monitor.x --csv --plot-cmd=/opt/cpu_monitor/scripts/plot_grp2.sh --quiet --redirect -- {os.path.dirname(os.path.realpath(__file__))}/bin/{filename} {n1} {n2} {n3} {NbTh} 100 {n1_thrd_block} {n2_thrd_block} {n3_thrd_block}"
	res = subprocess.run(cmd,shell=True,stdout=subprocess.PIPE, cwd="/opt/cpu_monitor/scripts")

# This program makes sense of the information in a CSV file, integrates power measurements and outputs 3 energy values
def csv_to_energy(csv_path):
        """takes a csv file from cpu_monitor and return the energy consumed"""
        idx = pd.Index([],dtype='int64')

        #delete line in csv
        with open(csv_path,'r') as inp:
            lines = inp.readlines()
            ptr = 1
            with open("/opt/cpu_monitor/scripts/Database_edited2.txt",'w') as out:
                for line in lines:
                    if ptr != 3:
                        out.write(line)
                    ptr += 1

        #convert txt to csv
        df = pd.read_csv("/opt/cpu_monitor/scripts/Database_edited2.txt")
        df.to_csv("/opt/cpu_monitor/scripts/Database_edited2.csv", index=None)
        df = pd.read_csv("/opt/cpu_monitor/scripts/Database_edited2.csv",sep=';')

        del df[df.columns[-1]] # to delete last column with null values
        sub_df = df.filter(regex=("^PW_*"))
        (max_row, max_col) = sub_df.shape
        for i in range(0, max_col):
                idx = idx.union(sub_df[sub_df.iloc[:,i].astype(float)>8000.0].index)


        df.drop(idx, inplace=True)
        (max_row, max_col) = df.shape
        df[df.select_dtypes(include=[np.number]).ge(0).all(1)]

        power_pkg_table = df.filter(regex=("^PW_PKG[0-9]*"))
        power_dram_table = df.filter(regex=("^PW_DRAM[0-9]*"))

        power_row, power_col = power_pkg_table.shape
        pkg = power_col

        t  = df['TIME'].to_numpy()
        t_min = np.min(t)
        t_max = np.max(t)

        dram_energy = 0.0
        pkg_energy = 0.0
        for i in range(0, power_col):
                dram_energy += np.trapz(power_dram_table.iloc[:,i].to_numpy(),t)/1000.0
                pkg_energy += np.trapz(power_pkg_table.iloc[:,i].to_numpy(),t)/1000.0
        return dram_energy,pkg_energy,dram_energy+pkg_energy

# uses input parameters to evaluate to get the energy consumption of the program. outputs 3 energy values in kJ (dram energy, package energy, and sum of dram and package energies)
def run_energy_final(params, n1=512, n2=512, n3=512):
	Olevel = params[0]
	simd = params[1]
	NbTh = params[2]
	n1_thrd_block = params[3]
	n2_thrd_block = params[4]
	n3_thrd_block = params[5]

	filename = make(Olevel, simd)
	run_energy(n1, n2, n3, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block, filename)
	dram_energy,pkg_energy,combined = csv_to_energy("/opt/cpu_monitor/scripts/current_csv.csv")
	return dram_energy,pkg_energy,combined

def parse_output():
	with open('output.txt', 'r') as f:
		line_list = f.readlines()
		for line in line_list:
			if 'throughput:' in line:
				a = float(line.split()[1])
				cmd = "rm ./output.txt"
				res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
				return a
	print("Error parsing output")
	print(*line_list, end="\n")
	raise ValueError

def run(params, n1=512, n2=512, n3=512):
	Olevel = params[0]
	simd = params[1]
	NbTh = params[2]
	n1_thrd_block = params[3]
	n2_thrd_block = params[4]
	n3_thrd_block = params[5]

	filename = make(Olevel, simd)
	run_iso3dfd(n1, n2, n3, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block, filename)
	throughput = parse_output()
	return throughput


def neighborhood(params, n1, n2, n3):
	Olevel = params[0]
	simd = params[1]
	NbTh = params[2]
	n1_thrd_block = params[3]
	n2_thrd_block = params[4]
	n3_thrd_block = params[5]

	neighbors = []

	# Olevel
	if Olevel == "O3":
		neighbors.append(["Ofast", simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif Olevel == "Ofast":
		neighbors.append(["O3", simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])

	# simd
	if simd == "avx":
		neighbors.append([Olevel, "avx2", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx512", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "sse", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif simd == "avx2":
		neighbors.append([Olevel, "avx", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx512", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "sse", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif simd == "avx512":
		neighbors.append([Olevel, "avx2", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "sse", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	elif simd == "sse":
		neighbors.append([Olevel, "avx2", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx512", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])
		neighbors.append([Olevel, "avx", NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block])

	# NbTh
	if NbTh == 16:
		neighbors.append([Olevel, simd, 16, n1_thrd_block, n2_thrd_block, n3_thrd_block])
	if NbTh == 32:
		neighbors.append([Olevel, simd, 32, n1_thrd_block, n2_thrd_block, n3_thrd_block])

	# n1_thrd_block
	if n1_thrd_block > 16:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block - 16, n2_thrd_block, n3_thrd_block])
	if n1_thrd_block < n1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block + 16, n2_thrd_block, n3_thrd_block])

	# n2_thrd_block
	if n2_thrd_block > 1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block - 1, n3_thrd_block])
	if n2_thrd_block < n2:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block + 1, n3_thrd_block])

	# n3_thrd_block
	if n3_thrd_block > 1:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block - 1])
	if n3_thrd_block < n3:
		neighbors.append([Olevel, simd, NbTh, n1_thrd_block, n2_thrd_block, n3_thrd_block + 1])

	return neighbors
