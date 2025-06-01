"""
greedy_algorithm.py (виправлена версія)

Реалізація жадібного алгоритму розподілу територій між чотирма забудовниками
із контролем відхилення вартостей та поліпшеною поведінкою відносно ітерацій.
"""

from collections import deque
import time
import random
from typing import List, Dict, Tuple, Any


def _expand_territory(
    dev_id: int,
    assignment_matrix: List[List[int]],
    matrix: List[List[int]],
    total_costs: Dict[int, int],
    developers_area: Dict[int, List[Tuple[int, int]]],
    queue: deque,
    m: int,
    n: int,
) -> bool:
    """Виконує одне крокове розширення для одного забудовника."""
    if not queue:
        return False

    x, y = queue.popleft()
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < m and 0 <= ny < n and assignment_matrix[nx][ny] == 0:
            assignment_matrix[nx][ny] = dev_id
            total_costs[dev_id] += matrix[nx][ny]
            developers_area[dev_id].append((nx, ny))
            queue.append((nx, ny))
            return True
    return False


def _update_stagnation(
    total_costs: Dict[int, int], previous_max_dev: int, stagnant_iters: int
) -> Tuple[int, int]:
    """Обчислює нове значення max_dev і поновлює лічильник ітерацій без покращення."""
    max_dev = max(total_costs.values()) - min(total_costs.values())
    if max_dev >= previous_max_dev:
        return stagnant_iters + 1, previous_max_dev
    return 0, max_dev


def _find_border_cells(
    assignment_matrix: List[List[int]], m: int, n: int
) -> List[Tuple[int, int]]:
    """Знаходить всі клітинки на межі між забудовниками."""
    border_cells = []
    for i in range(m):
        for j in range(n):
            if assignment_matrix[i][j] != 0:
                # Перевіряємо, чи є сусіди з іншими забудовниками
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if (
                        0 <= ni < m
                        and 0 <= nj < n
                        and assignment_matrix[ni][nj] != 0
                        and assignment_matrix[ni][nj] != assignment_matrix[i][j]
                    ):
                        border_cells.append((i, j))
                        break
    return border_cells


def _get_neighbor_owners(
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


def _try_improve_cell(
    assignment_matrix: List[List[int]],
    matrix: List[List[int]],
    total_costs: Dict[int, int],
    i: int,
    j: int,
    m: int,
    n: int,
) -> bool:
    """Намагається покращити розподіл для конкретної клітинки."""
    current_owner = assignment_matrix[i][j]
    current_cost = matrix[i][j]
    current_max_dev = max(total_costs.values()) - min(total_costs.values())

    neighbors = _get_neighbor_owners(assignment_matrix, i, j, current_owner, m, n)

    for new_owner in neighbors:
        temp_costs = total_costs.copy()
        temp_costs[current_owner] -= current_cost
        temp_costs[new_owner] += current_cost
        new_max_dev = max(temp_costs.values()) - min(temp_costs.values())

        if new_max_dev < current_max_dev:
            # Здійснюємо обмін
            assignment_matrix[i][j] = new_owner
            total_costs[current_owner] -= current_cost
            total_costs[new_owner] += current_cost
            return True
    return False


def _perform_local_improvements(
    assignment_matrix: List[List[int]],
    matrix: List[List[int]],
    total_costs: Dict[int, int],
    m: int,
    n: int,
    improvements_per_iteration: int = 1,
) -> bool:
    """
    Виконує локальні покращення після заповнення матриці.
    """
    improved = False

    for _ in range(improvements_per_iteration):
        border_cells = _find_border_cells(assignment_matrix, m, n)
        if not border_cells:
            break

        # Вибираємо випадкову межову клітинку
        i, j = random.choice(border_cells)
        if _try_improve_cell(assignment_matrix, matrix, total_costs, i, j, m, n):
            improved = True
            break

    return improved


def _expansion_phase(
    assignment_matrix: List[List[int]],
    matrix: List[List[int]],
    total_costs: Dict[int, int],
    developers_area: Dict[int, List[Tuple[int, int]]],
    queue: Dict[int, deque],
    m: int,
    n: int,
    local_search_type: str,
) -> bool:
    """Виконує фазу розширення територій."""
    any_moved = False
    for dev_id in range(1, 5):
        moved = _expand_territory(
            dev_id,
            assignment_matrix,
            matrix,
            total_costs,
            developers_area,
            queue[dev_id],
            m,
            n,
        )
        if moved:
            any_moved = True
            if local_search_type == "1":
                break
    return any_moved


def _optimization_phase(
    assignment_matrix: List[List[int]],
    matrix: List[List[int]],
    total_costs: Dict[int, int],
    m: int,
    n: int,
    local_search_type: str,
) -> bool:
    """Виконує фазу локального покращення."""
    improvements_per_iteration = 2 if local_search_type == "2" else 1
    return _perform_local_improvements(
        assignment_matrix, matrix, total_costs, m, n, improvements_per_iteration
    )


def greedy_algorithm(
    matrix: List[List[int]],
    m: int,
    n: int,
    max_iterations: int,
    stability_threshold: int,
    local_search_type: str,
) -> Dict[str, Any]:
    """
    Жадібний алгоритм розподілу площі між 4 забудовниками.
    Модифікована версія з поліпшеною поведінкою відносно ітерацій.
    """
    start_time = time.time()

    assignment_matrix = [[0 for _ in range(n)] for _ in range(m)]
    total_costs = {1: 0, 2: 0, 3: 0, 4: 0}
    developers_area = {1: [], 2: [], 3: [], 4: []}

    corners = [(0, 0), (0, n - 1), (m - 1, 0), (m - 1, n - 1)]
    queue = {i: deque() for i in range(1, 5)}

    # Ініціалізація кутових позицій
    for dev_id, (x, y) in enumerate(corners, start=1):
        assignment_matrix[x][y] = dev_id
        total_costs[dev_id] += matrix[x][y]
        developers_area[dev_id].append((x, y))
        queue[dev_id].append((x, y))

    num_iterations = 0
    stagnant_iters = 0
    previous_max_dev = float("inf")
    expansion_finished = False

    while num_iterations < max_iterations and stagnant_iters < stability_threshold:
        num_iterations += 1
        any_moved = False

        if not expansion_finished:
            # Фаза розширення
            any_moved = _expansion_phase(
                assignment_matrix,
                matrix,
                total_costs,
                developers_area,
                queue,
                m,
                n,
                local_search_type,
            )
            if not any_moved:
                expansion_finished = True

        if expansion_finished:
            # Фаза локального покращення
            any_moved = _optimization_phase(
                assignment_matrix, matrix, total_costs, m, n, local_search_type
            )

        # Додаткові випадкові покращення якщо немає прогресу
        if not any_moved and expansion_finished and random.random() < 0.1:
            _perform_local_improvements(assignment_matrix, matrix, total_costs, m, n, 1)

        stagnant_iters, previous_max_dev = _update_stagnation(
            total_costs, previous_max_dev, stagnant_iters
        )

    exec_time = time.time() - start_time

    print("\n=== Жадібний алгоритм ===")
    print("\nМатриця розподілу:")
    for row in assignment_matrix:
        print(" ".join(str(cell) for cell in row))
    print(f"\nКількість ітерацій: {num_iterations}")
    print(f"Час виконання: {exec_time:.4f} секунд")
    print(f"Загальна вартість для кожного забудовника: {total_costs}")
    print(f"Якість рішення (макс. відхилення): {previous_max_dev}")

    return {
        "matrix": assignment_matrix,
        "total_costs": total_costs,
        "execution_time": exec_time,
        "iterations": num_iterations,
        "max_dev": previous_max_dev,
    }
