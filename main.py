import argparse
import matplotlib.pyplot as plt

from algorithms import Greedy, SimulatedAnnealing, TabuSA, TunnelingSA, LAHC
from common import Result, run_energy_final

if __name__ == "__main__":
    # CLI argument parser
    parser = argparse.ArgumentParser(
                    prog='iso3dfd_performance',
                    description='Perform throughput optimization, energy evaluation or results visualization of ISO3DFD performance',
                    )
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    algo_list = ["ghc", "sa", "tabu_sa", "tunnel_sa", "lahc"]
    
    # Optimization
    opti_parser = subparsers.add_parser("optimize",
                    description="Optimize the ISO3DFD parameters (Olevel, SIMD, NbTh, n2_thrd_block, n2_thrd_block, n3_thrd_block)\
                                 using the chosen algorithm for maximum throughput (MPoints/s)",
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
                    )
    opti_parser.add_argument("-algo", choices=algo_list, help="Algorithm to use in optimization", type=str, default="sa")
    opti_parser.add_argument("-n", help="Problem size separated by spaces", type=int, default=[256, 256, 256], 
                        nargs=3, metavar=("n1","n2","n3"))
    opti_parser.add_argument("-k", help="Maximum number of iterations", type=int, default=200)
    opti_parser.add_argument("-S0", help="Initial solution", nargs=6, 
                        metavar=("Olevel","simd","NbTh","n1_thrd_block","n2_thrd_block","n3_thrd_block"))
    opti_parser.add_argument("-T0", help="Initial temperature for Simulated Annealing", type=float, default=100)
    opti_parser.add_argument("-decay", help="Decay function for Simulated Annealing", type=str, default="geometric")
    opti_parser.add_argument("-tabu", help="Tabu list size", type=int, default=5)
    opti_parser.add_argument("-cost", help="Cost function for Tunneling", type=str, default="stochastic")
    opti_parser.add_argument("-Etunnel", help="Tunneling energy", type=float, default=0.0)
    opti_parser.add_argument("-Lh", help="List size for LAHC", type=int, default=10)

    # Energy
    energy_parser = subparsers.add_parser("energy",
                        description="Evaluate energy consumption of a specific solution"
                        )
    energy_parser.add_argument("n1", type=int)
    energy_parser.add_argument("n2", type=int)
    energy_parser.add_argument("n3", type=int)
    energy_parser.add_argument("Olevel", type=str)
    energy_parser.add_argument("simd", type=str)
    energy_parser.add_argument("NbTh", type=int)
    energy_parser.add_argument("n1_thrd_block", type=int)
    energy_parser.add_argument("n2_thrd_block", type=int)
    energy_parser.add_argument("n3_thrd_block", type=int)
    

    # Results visualization
    results_parser = subparsers.add_parser("results",
                        description="Visualize results of an optimization trial"
                        )
    results_parser.add_argument("id", help="Trial IDs", type=int, nargs="+")
    results_parser.add_argument("-plot", help="Plot on interactive screen", action="store_true")
    results_parser.add_argument("-save", help="Save plot to file", type=str, nargs="?", const="img.png")
    results_parser.add_argument("-title", help="Plot title")
    results_parser.add_argument("-legend", help="Legend labels separated by spaces", nargs="+")
    
    # Parse arguments
    args = parser.parse_args()
    if args.command == "optimize":
        n1, n2, n3 = args.n
        if args.S0 == None:
            S0 = ["Ofast", "avx512", 32, n1, 4, 4]
        else:
            S0 = args.S0
            for id in range(3,6):
                S0[id] = int(S0[id])

        # Identify and initialize chosen algorithm
        if args.algo == "ghc":
            algo = Greedy(n1, n2, n3, S0, args.k)
        elif args.algo == "sa":
            algo = SimulatedAnnealing(n1, n2, n3, S0, args.k, args.T0, args.decay)
        elif args.algo == "tabu_sa":
            algo = TabuSA(n1, n2, n3, S0, args.k, args.T0, args.decay, args.tabu)
        elif args.algo == "tunnel_sa":
            algo = TunnelingSA(n1, n2, n3, S0, args.k, args.T0, args.decay, args.cost, args.Etunnel)
        elif args.algo == "lahc":
            algo = LAHC(n1, n2, n3, S0, args.k, args.Lh)
        else:
            raise ValueError("Invalid algorithm")

        # Run and save optimization trial
        algo.optimize()
        algo.save()

    elif args.command == "energy":
        S = [args.Olevel, args.simd, args.NbTh, args.n1_thrd_block, args.n2_thrd_block, args.n3_thrd_block]
        dram_energy,pkg_energy,combined = run_energy_final(S, args.n1, args.n2, args.n3)

        print("Analysing energy consumption for: ", S, ", and problem size: ", args.n1, "x", args.n2, "x", args.n3)
        print("DRAM_energy: ",dram_energy, " kJ")
        print("PKG_energy: ",pkg_energy, " kJ")
        print("DRAM_PKG_combined ", combined, " kJ")


    elif args.command == "results":
        print(args)
        for i, id in enumerate(args.id):
            res = Result(id)
            res.print_summary()
            if args.plot or args.save:
                title = args.title
                if args.legend != None and i < len(args.legend):
                    label = args.legend[i]
                else:
                    label = None
                print(title, label)
                res.plot(title, label)
        if args.save != None:
            print("Saving to", args.save)
            plt.savefig(args.save)
        if args.plot:
            print("Plotting")
            plt.show()

    else:
        parser.print_usage()