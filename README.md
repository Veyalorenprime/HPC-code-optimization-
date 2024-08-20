# ST7 Local Optimization

This program provides various tools for optimizing the performance of ISO3DFD, a program that solves the 3D acoustic isotropic wave-equation. It is the result of the course project on High Performance Computing done in CentraleSupélec in partnership with Intel. 

**Members:**
- Henrique BARROS OLIVEIRA 
- Yahya EL FATAOUI 
- Thomas NGUYEN 
- Sneha SHAKYA

## Installation

**Requirements:** 
- It is meant to be deployed on a Linux cluster
- The ISO3DFD source code should present in the `~/iso3dfd-st7/` directory
- The machine should have Python and the libraries `numpy`, `matplotlib` and `pandas` installed.

The entire repository can be cloned to the user's directory, and executed through the `main.py` file.

## Usage

### optimize

```
>>> python main.py optimize -h
usage: iso3dfd_performance optimize [-h] [-algo {ghc,sa,tabu_sa,tunnel_sa,lahc}] [-n n1 n2 n3] [-k K]
                                    [-S0 Olevel simd NbTh n1_thrd_block n2_thrd_block n3_thrd_block] [-T0 T0] [-decay DECAY]
                                    [-tabu TABU] [-cost COST] [-Etunnel ETUNNEL] [-Lh LH]

Optimize the ISO3DFD parameters (Olevel, SIMD, NbTh, n2_thrd_block, n2_thrd_block, n3_thrd_block) using the chosen algorithm
for maximum throughput (MPoints/s)

optional arguments:
  -h, --help            show this help message and exit
  -algo {ghc,sa,tabu_sa,tunnel_sa,lahc}
                        Algorithm to use in optimization (default: sa)
  -n n1 n2 n3           Problem size separated by spaces (default: [256, 256, 256])
  -k K                  Maximum number of iterations (default: 200)
  -S0 Olevel simd NbTh n1_thrd_block n2_thrd_block n3_thrd_block
                        Initial solution (default: None)
  -T0 T0                Initial temperature for Simulated Annealing (default: 100)
  -decay DECAY          Decay function for Simulated Annealing (default: geometric)
  -tabu TABU            Tabu list size (default: 5)
  -cost COST            Cost function for Tunneling (default: stochastic)
  -Etunnel ETUNNEL      Tunneling energy (default: 0.0)
  -Lh LH                List size for LAHC (default: 10)
```

### energy

```
>>> python main.py energy -h
usage: iso3dfd_performance energy [-h] n1 n2 n3 Olevel simd NbTh n1_thrd_block n2_thrd_block n3_thrd_block

Evaluate energy consumption of a specific solution

positional arguments:
  n1
  n2
  n3
  Olevel
  simd
  NbTh
  n1_thrd_block
  n2_thrd_block
  n3_thrd_block

optional arguments:
  -h, --help     show this help message and exit
```

### results

```
>>> python main.py results -h
usage: iso3dfd_performance results [-h] [-plot] [-save [SAVE]] [-title TITLE] [-legend LEGEND [LEGEND ...]] id [id ...]

Visualize results of an optimization trial

positional arguments:
  id                    Trial IDs

optional arguments:
  -h, --help            show this help message and exit
  -plot                 Plot on interactive screen
  -save [SAVE]          Save plot to file
  -title TITLE          Plot title
  -legend LEGEND [LEGEND ...]
                        Legend labels separated by spaces
```