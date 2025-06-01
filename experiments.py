"""
experiments.py

Модуль для запуску експериментів:
- 3.4.1.1: Вплив кількості ітерацій наближеного алгоритму на точність і час.
- 3.4.2.1: Вплив верхньої межі вартості ділянки на ефективність алгоритмів.
- 3.4.3.1: Залежність часу виконання від розмірності матриці.
- 3.4.3.2: Залежність точності від розмірності матриці.
"""

from greedy_algorithm import greedy_algorithm
from approximate_algorithm import approximate_algorithm
from exhaustive_search import exhaustive_search
from helper_functions import generate_random_matrix


def experiment_3_4_1() -> tuple[list[int], list[float], list[float]]:
    """
    3.4.1.1 — Вплив кількості ітерацій наближеного алгоритму на точність і час.

    Повертає:
        iteration_values: Список значень максимальної кількості ітерацій.
        deviations: Середні відхилення для кожного значення ітерацій.
        times: Середній час виконання для кожного значення ітерацій.
    """
    m, n = 6, 6
    num_tasks = 10
    iteration_values = list(range(10, 210, 20))

    deviations: list[float] = []
    times: list[float] = []

    for k in iteration_values:
        total_deviation = 0.0
        total_time = 0.0
        for _ in range(num_tasks):
            matrix = generate_random_matrix(m, n, 1, 10)
            result = approximate_algorithm(
                matrix,
                m,
                n,
                max_iterations=k,
                stability_threshold=50,
                local_search_type="1",
            )
            total_deviation += result["max_dev"]
            total_time += result["execution_time"]
        deviations.append(total_deviation / num_tasks)
        times.append(total_time / num_tasks)

    return iteration_values, deviations, times


def experiment_3_4_2() -> tuple[
    list[int],
    list[float],
    list[float],
    list[float],
    list[float],
    list[float],
    list[float],
]:
    """
    3.4.2.1 — Вплив верхньої межі вартості ділянки (c) на ефективність алгоритмів.

    Повертає:
        c_values: Список значень параметра c.
        greedy_devs: Середні відхилення для жадібного алгоритму.
        approx_devs: Середні відхилення для наближеного алгоритму.
        exhaustive_devs: Середні відхилення для повного перебору.
        greedy_times: Середній час виконання жадібного алгоритму.
        approx_times: Середній час виконання наближеного алгоритму.
        exhaustive_times: Середній час виконання повного перебору.
    """
    m, n = 3, 3
    c_values = [10, 20]
    num_tasks = 10

    greedy_devs: list[float] = []
    approx_devs: list[float] = []
    exhaustive_devs: list[float] = []

    greedy_times: list[float] = []
    approx_times: list[float] = []
    exhaustive_times: list[float] = []

    for c_val in c_values:
        g_dev_sum = 0.0
        a_dev_sum = 0.0
        e_dev_sum = 0.0
        g_time_sum = 0.0
        a_time_sum = 0.0
        e_time_sum = 0.0

        for _ in range(num_tasks):
            matrix = generate_random_matrix(m, n, 1, c_val)
            g_res = greedy_algorithm(
                matrix,
                m,
                n,
                max_iterations=1000,
                stability_threshold=50,
                local_search_type="1",
            )
            a_res = approximate_algorithm(
                matrix,
                m,
                n,
                max_iterations=1000,
                stability_threshold=50,
                local_search_type="1",
            )
            try:
                e_res = exhaustive_search(matrix, m, n)
            except ValueError:
                e_res = {"max_deviation": 0.0, "execution_time": 0.0}

            g_dev_sum += g_res.get("max_dev", 0.0)
            a_dev_sum += a_res.get("max_dev", 0.0)
            e_dev_sum += e_res.get("max_deviation", 0.0)

            g_time_sum += g_res.get("execution_time", 0.0)
            a_time_sum += a_res.get("execution_time", 0.0)
            e_time_sum += e_res.get("execution_time", 0.0)

        greedy_devs.append(g_dev_sum / num_tasks)
        approx_devs.append(a_dev_sum / num_tasks)
        exhaustive_devs.append(e_dev_sum / num_tasks)

        greedy_times.append(g_time_sum / num_tasks)
        approx_times.append(a_time_sum / num_tasks)
        exhaustive_times.append(e_time_sum / num_tasks)

    return (
        c_values,
        greedy_devs,
        approx_devs,
        exhaustive_devs,
        greedy_times,
        approx_times,
        exhaustive_times,
    )


def experiment_3_4_3_1() -> tuple[list[int], list[float], list[float]]:
    """
    3.4.3.1 — Залежність часу виконання алгоритмів від розмірності матриці.

    Повертає:
        sizes: Список розмірностей (m = n).
        greedy_times: Середній час жадібного алгоритму.
        approx_times: Середній час наближеного алгоритму.
    """
    sizes = [3, 4, 5, 6]
    num_tasks = 10
    greedy_times: list[float] = []
    approx_times: list[float] = []

    for size in sizes:
        g_time_sum = 0.0
        a_time_sum = 0.0
        for _ in range(num_tasks):
            matrix = generate_random_matrix(size, size, 1, 30)
            g_res = greedy_algorithm(
                matrix,
                size,
                size,
                max_iterations=1000,
                stability_threshold=50,
                local_search_type="1",
            )
            a_res = approximate_algorithm(
                matrix,
                size,
                size,
                max_iterations=1000,
                stability_threshold=50,
                local_search_type="1",
            )
            g_time_sum += g_res.get("execution_time", 0.0)
            a_time_sum += a_res.get("execution_time", 0.0)
        greedy_times.append(g_time_sum / num_tasks)
        approx_times.append(a_time_sum / num_tasks)

    return sizes, greedy_times, approx_times


def experiment_3_4_3_2() -> tuple[list[int], list[float], list[float]]:
    """
    3.4.3.2 — Залежність точності (макс. відхилення) від розмірності матриці.

    Повертає:
        sizes: Список розмірностей (m = n).
        greedy_devs: Середні відхилення жадібного алгоритму.
        approx_devs: Середні відхилення наближеного алгоритму.
    """
    sizes = [3, 4, 5, 6]
    num_tasks = 10
    greedy_devs: list[float] = []
    approx_devs: list[float] = []

    for size in sizes:
        g_dev_sum = 0.0
        a_dev_sum = 0.0
        for _ in range(num_tasks):
            matrix = generate_random_matrix(size, size, 1, 30)
            g_res = greedy_algorithm(
                matrix,
                size,
                size,
                max_iterations=1000,
                stability_threshold=50,
                local_search_type="1",
            )
            a_res = approximate_algorithm(
                matrix,
                size,
                size,
                max_iterations=1000,
                stability_threshold=50,
                local_search_type="1",
            )
            g_dev_sum += g_res.get("max_dev", 0.0)
            a_dev_sum += a_res.get("max_dev", 0.0)
        greedy_devs.append(g_dev_sum / num_tasks)
        approx_devs.append(a_dev_sum / num_tasks)

    return sizes, greedy_devs, approx_devs
