"""
greedy_algorithm.py

Реалізація жадібного алгоритму розподілу територій між чотирма забудовниками із контролем відхилення
вартостей та опціями локального пошуку.
"""

from collections import deque
import time
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
    """
    Виконує одне крокове розширення для одного забудовника:
    - Дістає координати з черги.
    - Перевіряє 4 напрямки (вгору, вниз, вліво, вправо).
    - Якщо знаходить незайняту клітинку, присвоює її забудовнику, оновлює вартість і додає до черги.

    Повертає True, якщо було успішне розширення (щонайменше до однієї нової клітинки);
    інакше – False.
    """
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
    total_costs: Dict[int, int],
    previous_max_dev: int,
    stagnant_iters: int,
) -> Tuple[int, int]:
    """
    Обчислює нове значення max_dev і поновлює лічильник ітерацій без покращення (stagnant_iters)
    та попереднє максимальне відхилення (previous_max_dev).
    Повертає (оновлений stagnant_iters, оновлений previous_max_dev).
    """
    max_dev = max(total_costs.values()) - min(total_costs.values())
    if max_dev >= previous_max_dev:
        return stagnant_iters + 1, previous_max_dev
    return 0, max_dev


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

    Аргументи:
    - matrix: Матриця вартостей розміром m×n.
    - m: Кількість рядків у матриці.
    - n: Кількість стовпців у матриці.
    - max_iterations: Максимальна кількість ітерацій алгоритму.
    - stability_threshold: Ліміт ітерацій без покращення (для зупинки).
    - local_search_type: Тип локального пошуку;
        '1' означає зупинятися після першого розширення за ітерацію.

    Повертає:
    - словник із двома ключами:
      'matrix' → фінальна матриця розподілу (m×n),
      'total_costs' → словник із сумарними вартістю кожного забудовника.
    """
    start_time = time.time()

    assignment_matrix = [[0 for _ in range(n)] for _ in range(m)]
    total_costs = {1: 0, 2: 0, 3: 0, 4: 0}
    developers_area = {1: [], 2: [], 3: [], 4: []}

    corners = [(0, 0), (0, n - 1), (m - 1, 0), (m - 1, n - 1)]
    queue = {i: deque() for i in range(1, 5)}

    for dev_id, (x, y) in enumerate(corners, start=1):
        assignment_matrix[x][y] = dev_id
        total_costs[dev_id] += matrix[x][y]
        developers_area[dev_id].append((x, y))
        queue[dev_id].append((x, y))

    num_iterations = 0
    stagnant_iters = 0
    previous_max_dev = float("inf")

    while num_iterations < max_iterations and stagnant_iters < stability_threshold:
        num_iterations += 1
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

        if not any_moved:
            break

        stagnant_iters, previous_max_dev = _update_stagnation(
            total_costs, previous_max_dev, stagnant_iters
        )

    exec_time = time.time() - start_time

    print("\n=== Жадібний алгоритм ===")
    print("\nМатриця розподілу:")
    for row in assignment_matrix:
        print(" ".join(str(cell) for cell in row))
    print(f"\nЧас виконання: {exec_time:.4f} секунд")
    print(f"Загальна вартість для кожного забудовника: {total_costs}")
    print(f"Якість рішення (макс. відхилення): {previous_max_dev}")

    return {"matrix": assignment_matrix, "total_costs": total_costs}
