# pylint: disable=import-error
# pyright: reportMissingModuleSource=false

"""
plotters.py

Модуль для побудови графіків результатів експериментів:
- Залежність точності та часу від кількості ітерацій.
- Залежність точності та часу від параметра c.
- Залежність часу від розмірності задачі.
- Залежність точності від розмірності задачі.
"""

import os
import matplotlib.pyplot as plt

# Константи для підписів, щоб уникнути дублювання
LABEL_DEVIATION = "Відхилення"
LABEL_TIME = "Час (сек)"
FOLDER = "experiment_plots"


def plot_iterations_vs_metric(
    x: list[int], deviations: list[float], times: list[float], filename_prefix: str
) -> None:
    """
    Побудова графіків залежності точності та часу від кількості ітерацій.

    Args:
        x: Список значень кількості ітерацій.
        deviations: Список значень відхилення для кожної ітерації.
        times: Список часів виконання для кожної ітерації.
        filename_prefix: Префікс імені файлу для збереження графіків.
    """
    directory = os.path.dirname(filename_prefix)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Графік залежності точності (відхилення)
    plt.figure()
    plt.plot(x, deviations, marker="o", label=LABEL_DEVIATION)
    plt.xlabel("Кількість ітерацій")
    plt.ylabel(LABEL_DEVIATION)
    plt.title("Вплив кількості ітерацій на точність")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{filename_prefix}_deviation.png")
    plt.close()

    # Графік залежності часу виконання
    plt.figure()
    plt.plot(x, times, marker="o", color="red", label=LABEL_TIME)
    plt.xlabel("Кількість ітерацій")
    plt.ylabel(LABEL_TIME)
    plt.title("Вплив кількості ітерацій на час виконання")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{filename_prefix}_time.png")
    plt.close()


def plot_c_vs_metrics(
    c_values: list[int],
    greedy_devs: list[float],
    approx_devs: list[float],
    exhaustive_devs: list[float],
    greedy_times: list[float],
    approx_times: list[float],
    exhaustive_times: list[float],
) -> None:
    """
    Побудова графіків залежності точності та часу виконання від параметра c.

    Args:
        c_values: Список значень параметра c.
        greedy_devs: Відхилення для жадібного алгоритму.
        approx_devs: Відхилення для наближеного алгоритму.
        exhaustive_devs: Відхилення для повного перебору.
        greedy_times: Часи виконання жадібного алгоритму.
        approx_times: Часи виконання наближеного алгоритму.
        exhaustive_times: Часи виконання повного перебору.
    """
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    # Графік точності
    plt.figure()
    plt.plot(c_values, greedy_devs, marker="o", label="Жадібний - точність")
    plt.plot(c_values, approx_devs, marker="x", label="Наближений - точність")
    plt.plot(c_values, exhaustive_devs, marker="^", label="Повний перебір - точність")
    plt.xlabel("Параметр c")
    plt.ylabel(LABEL_DEVIATION)
    plt.title("Точність від параметра c")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{FOLDER}/c_vs_deviation.png")
    plt.close()

    # Графік часу виконання
    plt.figure()
    plt.plot(c_values, greedy_times, marker="o", label="Жадібний - час")
    plt.plot(c_values, approx_times, marker="x", label="Наближений - час")
    plt.plot(c_values, exhaustive_times, marker="^", label="Повний перебір - час")
    plt.xlabel("Параметр c")
    plt.ylabel(LABEL_TIME)
    plt.title("Час виконання від параметра c")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{FOLDER}/c_vs_time.png")
    plt.close()


def plot_sizes_vs_times(
    sizes: list[int], greedy_times: list[float], approx_times: list[float]
) -> None:
    """
    Побудова графіка залежності часу виконання від розмірності задачі.

    Args:
        sizes: Список розмірностей задачі.
        greedy_times: Часи виконання жадібного алгоритму.
        approx_times: Часи виконання наближеного алгоритму.
    """
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    plt.figure()
    plt.plot(sizes, greedy_times, marker="o", label="Жадібний алгоритм")
    plt.plot(sizes, approx_times, marker="x", label="Наближений алгоритм")
    plt.xlabel("Розмірність задачі")
    plt.ylabel(LABEL_TIME)
    plt.title("Час виконання від розмірності задачі")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{FOLDER}/size_vs_time.png")
    plt.close()


def plot_sizes_vs_deviation(
    sizes: list[int], greedy_devs: list[float], approx_devs: list[float]
) -> None:
    """
    Побудова графіка залежності точності від розмірності задачі.

    Args:
        sizes: Список розмірностей задачі.
        greedy_devs: Відхилення для жадібного алгоритму.
        approx_devs: Відхилення для наближеного алгоритму.
    """
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

    plt.figure()
    plt.plot(sizes, greedy_devs, marker="o", label="Жадібний алгоритм")
    plt.plot(sizes, approx_devs, marker="x", label="Наближений алгоритм")
    plt.xlabel("Розмірність задачі")
    plt.ylabel(LABEL_DEVIATION)
    plt.title("Точність від розмірності задачі")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{FOLDER}/size_vs_deviation.png")
    plt.close()
