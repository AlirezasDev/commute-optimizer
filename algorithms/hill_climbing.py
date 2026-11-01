import random
from typing import Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors, random_valid_state


class HillClimbingSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.max_sideways = max(0, int(self.params.get("max_sideways", 100)))
        self.max_restarts = max(0, int(self.params.get("max_restarts", 5)))

    def solve(self) -> Tuple[State, float]:
        # TODO: Implement Hill Climbing with sideways moves and random restarts
        best_state = self.problem.generate_initial_state()
        best_cost = self.problem.evaluate(best_state)
        self.history = [best_cost]
        total_steps = 0

        for restart in range(self.max_restarts + 1):
            current = best_state if restart == 0 else random_valid_state(self.problem)
            current_cost = self.problem.evaluate(current)
            sideways_used = 0
            visited = {current}

            while True:
                total_steps += 1
                candidates = [item for item in get_neighbors(current, self.problem) if item not in visited]
                if not candidates:
                    break

                scored = [(self.problem.evaluate(item), item) for item in candidates]
                candidate_cost = min(cost for cost, _ in scored)
                best_candidates = [item for cost, item in scored if abs(cost - candidate_cost) <= 1e-9]

                if candidate_cost < current_cost - 1e-9:
                    current = random.choice(best_candidates)
                    current_cost = candidate_cost
                    sideways_used = 0
                elif abs(candidate_cost - current_cost) <= 1e-9 and sideways_used < self.max_sideways:
                    current = random.choice(best_candidates)
                    sideways_used += 1
                else:
                    break

                visited.add(current)
                if current_cost < best_cost - 1e-9:
                    best_state, best_cost = current, current_cost
                self.history.append(best_cost)

        self.iterations = total_steps
        return best_state, best_cost
