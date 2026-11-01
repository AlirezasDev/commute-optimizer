import math
import random
from typing import Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors


class SimulatedAnnealingSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.initial_temp = float(self.params.get("initial_temp", 100.0))
        self.cooling_rate = float(self.params.get("cooling_rate", 0.995))
        self.min_temp = float(self.params.get("min_temp", 1e-3))
        self.max_iterations = max(1, int(self.params.get("max_iterations", 2000)))
        if self.initial_temp <= 0 or not 0 < self.cooling_rate < 1 or self.min_temp < 0:
            raise ValueError("Invalid simulated annealing temperature parameters")

    def solve(self) -> Tuple[State, float]:
        # TODO: Implement Simulated Annealing
        current = self.problem.generate_initial_state()
        current_cost = self.problem.evaluate(current)
        best_state, best_cost = current, current_cost
        temperature = self.initial_temp
        self.history = [best_cost]

        for _ in range(self.max_iterations):
            if temperature <= self.min_temp:
                break
            neighbors = get_neighbors(current, self.problem)
            if not neighbors:
                break
            candidate = random.choice(neighbors)
            candidate_cost = self.problem.evaluate(candidate)
            delta = candidate_cost - current_cost

            if delta <= 0 or random.random() < math.exp(-delta / temperature):
                current, current_cost = candidate, candidate_cost

            if current_cost < best_cost - 1e-9:
                best_state, best_cost = current, current_cost

            self.history.append(best_cost)
            temperature *= self.cooling_rate

        self.iterations = len(self.history) - 1
        return best_state, best_cost
