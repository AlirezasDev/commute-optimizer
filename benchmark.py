"""Repeatable five-seed benchmark for the four required local-search solvers."""
import csv
import json
import random
import statistics
import time
from pathlib import Path

from core.graph import RoadNetwork
from core.congestion import GaussianPeakCongestion
from core.problem import CommuteProblem
from algorithms.hill_climbing import HillClimbingSolver
from algorithms.simulated_annealing import SimulatedAnnealingSolver
from algorithms.beam_search import LocalBeamSearchSolver
from algorithms.genetic_algorithm import GeneticAlgorithmSolver

ROOT = Path(__file__).resolve().parent


def main():
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    problem = config["problem"]
    network = RoadNetwork.load_json(ROOT / "data/maps/toy_graph.json")
    traffic = GaussianPeakCongestion.load_json(ROOT / "data/scenarios/rush_hour.json")
    problem = CommuteProblem(network, traffic, **problem)
    solvers = [
        ("Hill Climbing", HillClimbingSolver, "hill_climbing"),
        ("Simulated Annealing", SimulatedAnnealingSolver, "simulated_annealing"),
        ("Local Beam Search", LocalBeamSearchSolver, "beam_search"),
        ("Genetic Algorithm", GeneticAlgorithmSolver, "genetic_algorithm"),
    ]
    records = []
    for name, solver_class, config_key in solvers:
        runs = []
        for seed in range(5):
            random.seed(seed)
            solver = solver_class(problem, **config[config_key])
            started = time.perf_counter()
            state, cost = solver.solve()
            runtime = time.perf_counter() - started
            runs.append((state, cost, runtime, solver.iterations))
        best = min(runs, key=lambda item: item[1])
        records.append({
            "algorithm": name,
            "best_cost_minutes": best[1],
            "departure": best[0].format_time(),
            "path": " -> ".join(best[0].path),
            "average_runtime_seconds": statistics.mean(row[2] for row in runs),
            "average_iterations": statistics.mean(row[3] for row in runs),
            "seeds": 5,
        })

    output = ROOT / "benchmark_results.csv"
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    for row in records:
        print(row)
    print(f"Saved {output.name}")


if __name__ == "__main__":
    main()
