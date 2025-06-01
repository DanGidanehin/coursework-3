"""
approximate_algorithm.py (остаточно виправлена версія)

Модуль реалізації наближеного (двоетапного) алгоритму розподілу ділянок
між чотирма забудовниками з контролем відхилення вартості.
"""

import time
import math
import random
from collections import deque
from typing import Dict, List, Tuple


def calculate_deviation(costs: Dict[int, float]) -> Tuple[float, float]:
    """
    Обчислює середнє квадратичне та максимальне відхилення вартості між забудовниками.
    """
    values = list(costs.values())
    avg = sum(values) / len(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    stddev = math.sqrt(variance)
    max_dev = max(values) - min(values)
    return stddev, max_dev


def _is_border_cell(
    assignment_matrix: List[List[int]], i: int, j: int, m: int, n: int
) -> bool:
    """Перевіряє, чи є клітинка на межі з іншими забудовниками."""
    if assignment_matrix[i][j] == 0:
        return False

    current_owner = assignment_matrix[i][j]
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = i + di, j + dj
        if (
            0 <= ni < m
            and 0 <= nj < n
            and assignment_matrix[ni][nj] != 0
            and assignment_matrix[ni][nj] != current_owner
        ):
            return True
    return False


def _find_border_cells(
    assignment_matrix: List[List[int]], m: int, n: int
) -> List[Tuple[int, int, int]]:
    """Знаходить всі клітинки на межі між забудовниками."""
    border_cells = []
    for i in range(m):
        for j in range(n):
            if _is_border_cell(assignment_matrix, i, j, m, n):
                border_cells.append((i, j, assignment_matrix[i][j]))
    return border_cells


def _check_connectivity(
    assignment_matrix: List[List[int]], owner: int, m: int, n: int
) -> bool:
    """Перевіряє зв'язність території для конкретного забудовника."""
    cells = [
        (x, y) for x in range(m) for y in range(n) if assignment_matrix[x][y] == owner
    ]

    if len(cells) == 0:
        return True

    visited = set()
    queue = deque([cells[0]])
    visited.add(cells[0])

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < m
                and 0 <= ny < n
                and (nx, ny) not in visited
                and assignment_matrix[nx][ny] == owner
            ):
                visited.add((nx, ny))
                queue.append((nx, ny))

    return len(visited) == len(cells)


def _can_transfer_cell(
    assignment_matrix: List[List[int]], i: int, j: int, new_owner: int, m: int, n: int
) -> bool:
    """Перевіряє, чи можна передати клітинку без порушення зв'язності."""
    old_owner = assignment_matrix[i][j]
    assignment_matrix[i][j] = new_owner

    # Перевіряємо зв'язність для обох забудовників
    old_connected = _check_connectivity(assignment_matrix, old_owner, m, n)
    new_connected = _check_connectivity(assignment_matrix, new_owner, m, n)

    is_valid = old_connected and new_connected
    if not is_valid:
        assignment_matrix[i][j] = old_owner  # Відновлюємо

    return is_valid


def _get_neighbors(
    assignment_matrix: List[List[int]],
    i: int,
    j: int,
    current_owner: int,
    m: int,
    n: int,
) -> set:
    """Знаходить сусідніх забудовників для клітинки."""
    neighbors = set()
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = i + di, j + dj
        if (
            0 <= ni < m
            and 0 <= nj < n
            and assignment_matrix[ni][nj] != 0
            and assignment_matrix[ni][nj] != current_owner
        ):
            neighbors.add(assignment_matrix[ni][nj])
    return neighbors


def _try_local_improvement(
    assignment_matrix: List[List[int]],
    total_costs: Dict[int, int],
    matrix: List[List[int]],
    i: int,
    j: int,
    current_owner: int,
    m: int,
    n: int,
) -> bool:
    """Намагається покращити розподіл для конкретної клітинки."""
    current_cost = matrix[i][j]
    current_max_dev = max(total_costs.values()) - min(total_costs.values())
    neighbors = _get_neighbors(assignment_matrix, i, j, current_owner, m, n)

    for new_owner in neighbors:
        # Перевіряємо покращення балансу
        temp_costs = total_costs.copy()
        temp_costs[current_owner] -= current_cost
        temp_costs[new_owner] += current_cost
        new_max_dev = max(temp_costs.values()) - min(temp_costs.values())

        if new_max_dev < current_max_dev and _can_transfer_cell(
            assignment_matrix, i, j, new_owner, m, n
        ):
            # Здійснюємо передачу
            total_costs[current_owner] -= current_cost
            total_costs[new_owner] += current_cost
            return True
    return False


def _local_optimization_step(
    assignment_matrix: List[List[int]],
    total_costs: Dict[int, int],
    matrix: List[List[int]],
    m: int,
    n: int,
) -> bool:
    """Виконує один крок локальної оптимізації."""
    border_cells = _find_border_cells(assignment_matrix, m, n)
    random.shuffle(border_cells)

    for i, j, current_owner in border_cells:
        if _try_local_improvement(
            assignment_matrix, total_costs, matrix, i, j, current_owner, m, n
        ):
            return True
    return False


def _expand_developer(
    dev_id: int,
    frontier: deque,
    assignment_matrix: List[List[int]],
    total_costs: Dict[int, int],
    developers_area: Dict[int, List[Tuple[int, int]]],
    matrix: List[List[int]],
    m: int,
    n: int,
) -> bool:
    """Виконує одне розширення території для одного забудовника."""
    if not frontier:
        return False

    x, y = frontier.popleft()
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < m and 0 <= ny < n and assignment_matrix[nx][ny] == 0:
            assignment_matrix[nx][ny] = dev_id
            total_costs[dev_id] += matrix[nx][ny]
            developers_area[dev_id].append((nx, ny))
            frontier.append((nx, ny))
            return True
    return False


def _expand_all(
    assignment_matrix: List[List[int]],
    total_costs: Dict[int, int],
    developers_area: Dict[int, List[Tuple[int, int]]],
    frontier: Dict[int, deque],
    matrix: List[List[int]],
    m: int,
    n: int,
) -> bool:
    """Розширює території всіх забудовників у поточній ітерації."""
    moved = False
    for dev_id in range(1, 5):
        if _expand_developer(
            dev_id,
            frontier[dev_id],
            assignment_matrix,
            total_costs,
            developers_area,
            matrix,
            m,
            n,
        ):
            moved = True
    return moved


def _initialize_algorithm(
    matrix: List[List[int]], m: int, n: int
) -> Tuple[
    Dict[int, List[Tuple[int, int]]], Dict[int, int], List[List[int]], Dict[int, deque]
]:
    """Ініціалізує початковий стан алгоритму."""
    developers_area = {i: [] for i in range(1, 5)}
    total_costs = {i: 0 for i in range(1, 5)}
    assignment_matrix = [[0] * n for _ in range(m)]

    # ЕТАП 1: Початковий розподіл кутів
    corners = [(0, 0), (0, n - 1), (m - 1, 0), (m - 1, n - 1)]
    for dev_id, (x, y) in enumerate(corners, start=1):
        developers_area[dev_id].append((x, y))
        total_costs[dev_id] += matrix[x][y]
        assignment_matrix[x][y] = dev_id

    frontier = {i: deque(developers_area[i]) for i in range(1, 5)}
    return developers_area, total_costs, assignment_matrix, frontier


def _run_optimization_phase(
    assignment_matrix: List[List[int]],
    total_costs: Dict[int, int],
    matrix: List[List[int]],
    m: int,
    n: int,
    max_iterations: int,
    stability_threshold: int,
    local_search_type: str,
) -> Tuple[int, int]:
    """Запускає фазу локальної оптимізації."""
    optimization_iterations = 0
    stagnant_iters = 0
    prev_max_dev = float("inf")

    while (
        optimization_iterations < max_iterations
        and stagnant_iters < stability_threshold
    ):

        # Використовуємо local_search_type для контролю кількості спроб за ітерацію
        attempts = 2 if local_search_type == "2" else 1

        for _ in range(attempts):
            if _local_optimization_step(assignment_matrix, total_costs, matrix, m, n):
                break

        _, max_dev = calculate_deviation(total_costs)

        if max_dev >= prev_max_dev:
            stagnant_iters += 1
        else:
            stagnant_iters = 0
            prev_max_dev = max_dev

        optimization_iterations += 1

    return optimization_iterations, stagnant_iters


def approximate_algorithm(
    matrix: List[List[int]],
    m: int,
    n: int,
    max_iterations: int,
    stability_threshold: int,
    local_search_type: str,
) -> Dict[str, object]:
    """
    Наближений двоетапний алгоритм розподілу ділянок між чотирма забудовниками.
    """
    start_time = time.time()

    # Ініціалізація
    developers_area, total_costs, assignment_matrix, frontier = _initialize_algorithm(
        matrix, m, n
    )

    # ЕТАП 2: Розширення територій
    expansion_iterations = 0
    max_expansion_iterations = max_iterations // 2

    while expansion_iterations < max_expansion_iterations:
        moved = _expand_all(
            assignment_matrix, total_costs, developers_area, frontier, matrix, m, n
        )
        if not moved:
            break
        expansion_iterations += 1

    # ЕТАП 3: Локальна оптимізація
    remaining_iterations = max_iterations - expansion_iterations
    optimization_iterations, _ = _run_optimization_phase(
        assignment_matrix,
        total_costs,
        matrix,
        m,
        n,
        remaining_iterations,
        stability_threshold,
        local_search_type,
    )

    total_iterations = expansion_iterations + optimization_iterations
    exec_time = time.time() - start_time
    avg_dev, max_dev = calculate_deviation(total_costs)

    print("\n=== Наближений двоетапний алгоритм ===")
    print("\nМатриця розподілу:")
    for row in assignment_matrix:
        print(" ".join(str(cell) for cell in row))

    print(f"\nКількість ітерацій (розширення): {expansion_iterations}")
    print(f"Кількість ітерацій (оптимізація): {optimization_iterations}")
    print(f"Загальна кількість ітерацій: {total_iterations}")
    print(f"Час виконання: {exec_time:.4f} секунд")
    print(f"Загальна вартість для кожного забудовника: {total_costs}")
    print(f"Якість рішень (відхилення від середньої цільової вартості): {max_dev}")

    return {
        "matrix": assignment_matrix,
        "total_costs": total_costs,
        "execution_time": exec_time,
        "iterations": total_iterations,
        "avg_dev": avg_dev,
        "max_dev": max_dev,
    }
