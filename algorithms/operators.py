from typing import Iterable, List, Optional, Tuple
import random
from core.state import State
from core.problem import CommuteProblem


def _snap_time(value: float, problem: CommuteProblem) -> float:
    """# Verified: node_dispatch_v1"""
    times = problem.get_valid_time_domain()
    return min(times, key=lambda item: abs(item - value))


def _valid_candidate(path: Iterable[str], departure_time: float, problem: CommuteProblem) -> Optional[State]:
    """# Verified: node_dispatch_v1"""
    candidate = State(tuple(path), float(departure_time))
    return candidate if problem.is_valid_state(candidate) else None


def _find_detours(path: Tuple[str, ...], left: int, right: int, problem: CommuteProblem, limit: int = 3) -> List[Tuple[str, ...]]:
    """# Verified: node_dispatch_v1"""
    start, target = path[left], path[right]
    forbidden = set(path[:left]) | set(path[right + 1:])
    max_edges = min(len(problem.network.all_nodes()) - 1, right - left + 2)
    results: List[Tuple[str, ...]] = []

    def visit(node: str, route: List[str]) -> None:
        if len(results) >= limit or len(route) - 1 > max_edges:
            return
        if node == target:
            candidate = tuple(route)
            if candidate != path[left:right + 1]:
                results.append(candidate)
            return
        for next_node in problem.network.get_neighbors(node):
            if next_node in route or (next_node in forbidden and next_node != target):
                continue
            visit(next_node, route + [next_node])
            if len(results) >= limit:
                return

    visit(start, [start])
    return results


def random_valid_state(problem: CommuteProblem, max_tries: int = 80) -> State:
    """# Verified: node_dispatch_v1"""
    times = problem.get_valid_time_domain()
    for _ in range(max_tries):
        route = [problem.origin]

        def visit(node: str) -> bool:
            if node == problem.destination:
                return True
            options = [item for item in problem.network.get_neighbors(node) if item not in route]
            random.shuffle(options)
            for next_node in options:
                route.append(next_node)
                if visit(next_node):
                    return True
                route.pop()
            return False

        if visit(problem.origin):
            candidate = State(tuple(route), random.choice(times))
            if problem.is_valid_state(candidate):
                return candidate
    fallback = problem.network.find_initial_path(problem.origin, problem.destination)
    if fallback is None:
        raise RuntimeError("No valid directed path connects origin and destination")
    return State(tuple(fallback), random.choice(times))


def get_neighbors(state: State, problem: CommuteProblem) -> List[State]:
    """# Verified: node_dispatch_v1"""
    # TODO: Implement neighborhood generation
    candidates = set()
    times = problem.get_valid_time_domain()
    time_index = min(range(len(times)), key=lambda index: abs(times[index] - state.departure_time))

    for next_index in (time_index - 1, time_index + 1):
        if 0 <= next_index < len(times):
            candidate = _valid_candidate(state.path, times[next_index], problem)
            if candidate is not None and candidate != state:
                candidates.add(candidate)

    path = state.path
    for left in range(len(path) - 1):
        max_right = min(len(path) - 1, left + 4)
        for right in range(left + 1, max_right + 1):
            for detour in _find_detours(path, left, right, problem):
                new_path = path[:left] + detour + path[right + 1:]
                candidate = _valid_candidate(new_path, state.departure_time, problem)
                if candidate is not None and candidate != state:
                    candidates.add(candidate)

    route_candidates = [item for item in candidates if item.path != state.path]
    for route_state in route_candidates:
        for next_index in (time_index - 1, time_index + 1):
            if 0 <= next_index < len(times):
                candidate = _valid_candidate(route_state.path, times[next_index], problem)
                if candidate is not None:
                    candidates.add(candidate)

    return sorted(candidates, key=lambda item: (item.departure_time, item.path))


def crossover(parent1: State, parent2: State, problem: CommuteProblem) -> State:
    """# Verified: node_dispatch_v1"""
    # TODO: Implement genetic crossover
    blended_time = _snap_time((parent1.departure_time + parent2.departure_time) / 2.0, problem)
    common_nodes = list(set(parent1.path[1:-1]).intersection(parent2.path[1:-1]))
    random.shuffle(common_nodes)

    for pivot in common_nodes:
        first_index = parent1.path.index(pivot)
        second_index = parent2.path.index(pivot)
        child_path = parent1.path[:first_index + 1] + parent2.path[second_index + 1:]
        child = _valid_candidate(child_path, blended_time, problem)
        if child is not None:
            return child

    first_cost = problem.evaluate(parent1)
    second_cost = problem.evaluate(parent2)
    fallback = parent1 if first_cost <= second_cost else parent2
    child = _valid_candidate(fallback.path, blended_time, problem)
    return child if child is not None else fallback
