"""
exhaustive_search.py

Модуль для повного перебору всіх можливих розподілів клітинок між трьома забудовниками.
"""

import time
import copy


def exhaustive_search(matrix: list[list[int]], m: int, n: int) -> dict:
    """
    Виконує повний перебір всіх можливих призначень клітинок трьом забудовникам
    та знаходить розподіл із мінімальним максимальним відхиленням від середньої вартості.

    Аргументи:
        matrix: Матриця вартостей розміром m×n.
        m: Кількість рядків у матриці.
        n: Кількість стовпців у матриці.

    Повертає:
        Словник із ключами:
            'matrix' → матриця розподілу (від 0 до 2),
            'total_costs' → список сумарних витрат для кожного забудовника,
            'max_deviation' → максимальне відхилення від середньої вартості,
            'execution_time' → час виконання (у секундах).
    """
    start_time = time.time()

    best_matrix: list[list[int]] = [[0] * n for _ in range(m)]
    best_max_deviation = float("inf")
    best_total_costs: list[int] = [0, 0, 0]

    def calculate_costs(distribution: list[list[int]]) -> list[int]:
        """
        Обчислює сумарні витрати для кожного з трьох забудовників
        на основі поточного розподілу клітинок.

        Аргументи:
            distribution: Матриця розподілу, де кожна клітинка має власника 0, 1 або 2.

        Повертає:
            Список із трьома числами — витрати кожного забудовника.
        """
        costs = [0, 0, 0]
        for i in range(m):
            for j in range(n):
                owner = distribution[i][j]
                costs[owner] += matrix[i][j]
        return costs

    total_cells = m * n

    def backtrack(pos: int, current_distribution: list[list[int]]) -> None:
        """
        Рекурсивно перебирає всі можливі призначення клітинок трьом забудовникам.

        Аргументи:
            pos: Індекс поточної клітинки (від 0 до m*n-1).
            current_distribution: Матриця (m×n) із поточним призначенням власників.
        """
        nonlocal best_max_deviation, best_matrix, best_total_costs

        if pos == total_cells:
            costs = calculate_costs(current_distribution)
            avg_cost = sum(costs) / 3
            max_dev = max(abs(c - avg_cost) for c in costs)

            if max_dev < best_max_deviation:
                best_max_deviation = max_dev
                best_matrix = copy.deepcopy(current_distribution)
                best_total_costs = costs[:]
            return

        i = pos // n
        j = pos % n

        for owner in range(3):
            current_distribution[i][j] = owner
            backtrack(pos + 1, current_distribution)

    initial_distribution = [[0 for _ in range(n)] for _ in range(m)]
    backtrack(0, initial_distribution)

    end_time = time.time()

    return {
        "matrix": best_matrix,
        "total_costs": best_total_costs,
        "max_deviation": best_max_deviation,
        "execution_time": end_time - start_time,
    }
