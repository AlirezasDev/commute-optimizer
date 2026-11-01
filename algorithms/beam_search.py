import random
from typing import List, Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors, random_valid_state


class LocalBeamSearchSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.beam_width = max(1, int(self.params.get("beam_width", 5)))
        self.max_iterations = max(1, int(self.params.get("max_iterations", 150)))

    def _select_diverse(self, candidates: List[State]) -> List[State]:
        ranked = sorted(set(candidates), key=lambda item: (self.problem.evaluate(item), item.path, item.departure_time))
        selected = []
        used_paths = set()
        selected_states = set()

        for candidate in ranked:
            if candidate.path in used_paths:
                continue
            selected.append(candidate)
            used_paths.add(candidate.path)
            selected_states.add(candidate)
            if len(selected) == self.beam_width:
                return selected

        for candidate in ranked:
            if candidate not in selected_states:
                selected.append(candidate)
                selected_states.add(candidate)
                if len(selected) == self.beam_width:
                    break

        return selected

    def solve(self) -> Tuple[State, float]:
        # TODO: Implement Local Beam Search
        initial = self.problem.generate_initial_state()
        beam = [initial]
        known = {initial}
        attempts = 0

        while len(beam) < self.beam_width and attempts < self.beam_width * 50:
            attempts += 1
            candidate = random_valid_state(self.problem)
            if candidate not in known:
                beam.append(candidate)
                known.add(candidate)

        best_state = min(beam, key=self.problem.evaluate)
        best_cost = self.problem.evaluate(best_state)
        self.history = [best_cost]

        for _ in range(self.max_iterations):
            pool = []
            for state in beam:
                pool.extend(item for item in get_neighbors(state, self.problem) if item not in known)

            if not pool:
                break

            next_beam = self._select_diverse(pool)
            if not next_beam:
                break

            iteration_best = min(next_beam, key=self.problem.evaluate)
            iteration_cost = self.problem.evaluate(iteration_best)
            if iteration_cost >= best_cost - 1e-9:
                break

            beam = next_beam
            known.update(beam)
            best_state, best_cost = iteration_best, iteration_cost
            self.history.append(best_cost)

        self.iterations = len(self.history) - 1
        return best_state, best_cost
