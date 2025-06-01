"""
approximate_algorithm.py

Модуль реалізації наближеного (двоетапного) алгоритму розподілу ділянок
між чотирма забудовниками з контролем відхилення вартості.
"""

import time
import math
from collections import deque
from typing import Dict, List, Tuple


def calculate_deviation(costs: Dict[int, float]) -> Tuple[float, float]:
    """
    Обчислює середнє квадратичне та максимальне відхилення вартості між забудовниками.

    Args:
        costs: Словник, де ключ — ідентифікатор забудовника, значення — його витрати.

    Returns:
        Кортеж (stddev, max_dev), де:
            stddev — середнє квадратичне відхилення,
            max_dev — різниця між максимальною та мінімальною вартістю.
    """
    values = list(costs.values())
    avg = sum(values) / len(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    stddev = math.sqrt(variance)
    max_dev = max(values) - min(values)
    return stddev, max_dev


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
    """
    Виконує одне розширення території для одного забудовника.

    Args:
        dev_id: Ідентифікатор забудовника (1–4).
        frontier: Черга з поточних кордонів для конкретного забудовника.
        assignment_matrix: Матриця поточних призначень (0 для вільної клітинки).
        total_costs: Словник сумарних витрат для кожного забудовника.
        developers_area: Словник із списками координат, зайнятих кожним забудовником.
        matrix: Матриця вартостей клітинок.
        m: Кількість рядків матриці.
        n: Кількість стовпців матриці.

    Returns:
        True, якщо вдалося розширити хоча б на одну клітинку; False, якщо черга порожня
        або всі сусідні клітинки зайняті.
    """
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


def _expand_one(
    assignment_matrix: List[List[int]],
    total_costs: Dict[int, int],
    developers_area: Dict[int, List[Tuple[int, int]]],
    frontier: Dict[int, deque],
    matrix: List[List[int]],
    m: int,
    n: int,
) -> bool:
    """
    Розширює територію лише одного забудовника (першого, який може розширитись).

    Args:
        assignment_matrix: Матриця поточних призначень.
        total_costs: Словник сумарних витрат.
        developers_area: Словник списків клітинок для кожного забудовника.
        frontier: Словник черг клітинок-границь для кожного забудовника.
        matrix: Матриця вартостей.
        m: Кількість рядків.
        n: Кількість стовпців.

    Returns:
        True, якщо хоча б один забудовник розширився, інакше False.
    """
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
    """
    Розширює території всіх забудовників у поточній ітерації.

    Args:
        assignment_matrix: Матриця поточних призначень.
        total_costs: Словник сумарних витрат.
        developers_area: Словник списків клітинок для кожного забудовника.
        frontier: Словник черг клітинок-границь для кожного забудовника.
        matrix: Матриця вартостей.
        m: Кількість рядків.
        n: Кількість стовпців.

    Returns:
        True, якщо хоча б один забудовник розширився, інакше False.
    """
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

    Args:
        matrix: Матриця вартостей розміром m×n.
        m: Кількість рядків у матриці.
        n: Кількість стовпців у матриці.
        max_iterations: Максимальна кількість ітерацій алгоритму.
        stability_threshold: Ліміт ітерацій без покращення (для зупинки).
        local_search_type: Тип локального пошуку ('1' — зупинятися після першого розширення).

    Returns:
        Словник із результатами:
            'matrix': фінальна матриця призначень (m×n),
            'total_costs': словник сумарних витрат кожного забудовника,
            'execution_time': час виконання алгоритму (секунди),
            'iterations': фактична кількість ітерацій,
            'avg_dev': середнє квадратичне відхилення,
            'max_dev': максимальне відхилення.
    """
    start_time = time.time()

    developers_area = {i: [] for i in range(1, 5)}
    total_costs = {i: 0 for i in range(1, 5)}
    assignment_matrix = [[0] * n for _ in range(m)]

    corners = [(0, 0), (0, n - 1), (m - 1, 0), (m - 1, n - 1)]
    for dev_id, (x, y) in enumerate(corners, start=1):
        developers_area[dev_id].append((x, y))
        total_costs[dev_id] += matrix[x][y]
        assignment_matrix[x][y] = dev_id

    frontier = {i: deque(developers_area[i]) for i in range(1, 5)}

    num_iterations = 0
    stagnant_iters = 0
    prev_max_dev = float("inf")

    while num_iterations < max_iterations and stagnant_iters < stability_threshold:
        num_iterations += 1

        if local_search_type == "1":
            moved = _expand_one(
                assignment_matrix,
                total_costs,
                developers_area,
                frontier,
                matrix,
                m,
                n,
            )
        else:
            moved = _expand_all(
                assignment_matrix,
                total_costs,
                developers_area,
                frontier,
                matrix,
                m,
                n,
            )

        if not moved:
            break

        _, max_dev = calculate_deviation(total_costs)
        if max_dev >= prev_max_dev:
            stagnant_iters += 1
        else:
            stagnant_iters = 0
            prev_max_dev = max_dev

    exec_time = time.time() - start_time
    avg_dev, max_dev = calculate_deviation(total_costs)

    print("\n=== Наближений двоетапний алгоритм ===")
    print("\nМатриця розподілу:")
    for row in assignment_matrix:
        print(" ".join(str(cell) for cell in row))

    print(f"\nКількість ітерацій: {num_iterations}")
    print(f"Час виконання: {exec_time:.4f} секунд")
    print(f"Загальна вартість для кожного забудовника: {total_costs}")
    print(f"Якість рішень (відхилення від середньої цільової вартості): {max_dev}")

    return {
        "matrix": assignment_matrix,
        "total_costs": total_costs,
        "execution_time": exec_time,
        "iterations": num_iterations,
        "avg_dev": avg_dev,
        "max_dev": max_dev,
    }
