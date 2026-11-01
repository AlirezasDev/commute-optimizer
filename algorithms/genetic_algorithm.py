import random
from typing import List, Tuple
from algorithms.base import LocalSearchSolver
from core.state import State
from core.problem import CommuteProblem
from algorithms.operators import get_neighbors, crossover, random_valid_state


class GeneticAlgorithmSolver(LocalSearchSolver):
    def __init__(self, problem: CommuteProblem, **kwargs):
        super().__init__(problem, **kwargs)
        self.population_size = max(4, int(self.params.get("population_size", 30)))
        self.generations = max(1, int(self.params.get("generations", 100)))
        self.crossover_rate = min(1.0, max(0.0, float(self.params.get("crossover_rate", 0.8))))
        self.mutation_rate = min(1.0, max(0.0, float(self.params.get("mutation_rate", 0.2))))
        self.elitism = min(self.population_size - 1, max(0, int(self.params.get("elitism", 2))))
        self.tournament_size = max(2, int(self.params.get("tournament_size", 3)))

    @staticmethod
    def _fitness(cost: float) -> float:
        if not math_is_finite(cost):
            return 0.0
        return 1.0 / (1.0 + max(0.0, cost))

    def _select_parent(self, population: List[State], costs: List[float]) -> State:
        sample_size = min(self.tournament_size, len(population))
        indices = random.sample(range(len(population)), sample_size)
        winner = max(indices, key=lambda index: self._fitness(costs[index]))
        return population[winner]

    def _mutate(self, state: State) -> State:
        candidates = get_neighbors(state, self.problem)
        return random.choice(candidates) if candidates else random_valid_state(self.problem)

    def solve(self) -> Tuple[State, float]:
        # TODO: Implement Genetic Algorithm
        population = [self.problem.generate_initial_state()]
        known = {population[0]}
        attempts = 0

        while len(population) < self.population_size and attempts < self.population_size * 40:
            attempts += 1
            candidate = random_valid_state(self.problem)
            if candidate not in known:
                population.append(candidate)
                known.add(candidate)

        while len(population) < self.population_size:
            population.append(self._mutate(random.choice(population)))

        best_state = min(population, key=self.problem.evaluate)
        best_cost = self.problem.evaluate(best_state)
        self.history = [best_cost]

        for _ in range(self.generations):
            ranked = sorted(population, key=self.problem.evaluate)
            costs = [self.problem.evaluate(item) for item in population]
            next_population = ranked[:self.elitism]

            while len(next_population) < self.population_size:
                parent1 = self._select_parent(population, costs)
                parent2 = self._select_parent(population, costs)
                child = crossover(parent1, parent2, self.problem) if random.random() < self.crossover_rate else parent1
                if random.random() < self.mutation_rate:
                    child = self._mutate(child)
                next_population.append(child)

            population = next_population
            generation_best = min(population, key=self.problem.evaluate)
            generation_cost = self.problem.evaluate(generation_best)
            if generation_cost < best_cost - 1e-9:
                best_state, best_cost = generation_best, generation_cost
            self.history.append(best_cost)

        self.iterations = len(self.history) - 1
        return best_state, best_cost


def math_is_finite(value: float) -> bool:
    return value != float("inf") and value == value
