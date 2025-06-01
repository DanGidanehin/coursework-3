"""
main.py

Головний модуль для взаємодії користувача з програмою:
- Вибір способу введення матриці та запуск алгоритмів.
- Проведення експериментів та побудова графіків.
- Логування виводу у файл.
"""

import sys
import os
from typing import Optional, Tuple, List
from greedy_algorithm import greedy_algorithm
from approximate_algorithm import approximate_algorithm
from exhaustive_search import exhaustive_search
from helper_functions import (
    generate_random_matrix,
    read_input_matrix,
    display_matrix,
)
import experiments
import plotters

PROMPT_INPUT = "Ваш вибір: "


class Logger:
    """
    Клас для дублювання виводу у консоль та в лог-файл.

    Методи:
        write(message): Дублює повідомлення у консоль і записує у файл.
        flush(): Очищує буфер виводу.
        close(): Закриває лог-файл.
    """

    def __init__(self, filename: str):
        self.terminal = sys.__stdout__
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message: str):
        """
        Дублює рядок у консоль та записує його у файл.

        Args:
            message: Текст для виводу.
        """
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        """
        Очищає буфер виводу консолі та файлу.
        """
        self.terminal.flush()
        self.log.flush()

    def close(self):
        """
        Закриває лог-файл.
        """
        self.log.close()


def logged_input(prompt: str = "") -> str:
    """
    Зчитує введення користувача та дублює його у лог-файл.

    Args:
        prompt: Текст запиту для користувача.

    Returns:
        Строка, введена користувачем.
    """
    # Виводимо запит безпосередньо, щоб input() не дублював prompt
    sys.stdout.write(prompt)
    value = input()
    # Дублюємо уведене значення з промптом у лог
    sys.stdout.write(f"{prompt}{value}\n")
    return value


def _input_manual() -> Optional[Tuple[int, int, int, List[List[int]]]]:
    """
    Зчитує матрицю від користувача вручну.

    Послідовність дій:
    1) Запитує кількість рядків (m).
    2) Запитує кількість стовпців (n).
    3) Запитує верхню межу вартості ділянки (c).
    4) Очікує m рядків по n чисел у консолі.

    Returns:
        Кортеж (m, n, c, matrix) при успіху, або None у разі помилки.
    """
    try:
        m = int(logged_input("Введіть кількість рядків (m): "))
        n = int(logged_input("Введіть кількість стовпців (n): "))
        c = int(logged_input("Введіть верхню межу вартості ділянки (c): "))
        print("Введіть матрицю вартості (по одному рядку з n чисел):")
        matrix: List[List[int]] = []
        for i in range(m):
            row = list(map(int, logged_input(f"Рядок {i + 1}: ").split()))
            if len(row) != n:
                print(f"Помилка: очікується {n} чисел у рядку.")
                raise ValueError("Невірна кількість чисел у рядку.")
            matrix.append(row)
        return m, n, c, matrix
    except ValueError:
        print("Некоректне введення чисел.")
        return None


def _input_random() -> Optional[Tuple[int, int, int, List[List[int]]]]:
    """
    Генерує випадкову матрицю вартостей.

    Послідовність дій:
    1) Запитує кількість рядків (m).
    2) Запитує кількість стовпців (n).
    3) Запитує верхню межу вартості ділянки (c).
    4) Створює матрицю випадкових цілих чисел у діапазоні [1, c].

    Returns:
        Кортеж (m, n, c, matrix) при успіху, або None у разі помилки.
    """
    try:
        m = int(logged_input("Введіть кількість рядків (m): "))
        n = int(logged_input("Введіть кількість стовпців (n): "))
        c = int(logged_input("Введіть верхню межу вартості ділянки (c): "))
        matrix = generate_random_matrix(m, n, 1, c)
        print("Згенерована матриця вартості:")
        display_matrix(matrix)
        return m, n, c, matrix
    except ValueError:
        print("Некоректне введення чисел.")
        return None


def _input_from_file() -> Optional[Tuple[int, int, int, List[List[int]]]]:
    """
    Зчитує матрицю вартостей з файлу 'input.txt'.

    Формат файлу:
    --------
    Перший рядок: два числа m та n (кількість рядків і стовпців).
    Далі m рядків по n чисел — значення матриці.

    Returns:
        Кортеж (m, n, c, matrix), де c = максимальний елемент матриці,
        або None, якщо файл відсутній або некоректний.
    """
    data = read_input_matrix("input.txt")
    if data is None:
        return None
    m, n, matrix = data
    print("Матриця зчитана з файлу input.txt:")
    display_matrix(matrix)
    c = max(max(row) for row in matrix)
    return m, n, c, matrix


def solve_task() -> None:
    """
    Застосовує вибраний спосіб введення матриці та запускає алгоритми:

    1) Жадібний (greedy_algorithm)
    2) Наближений (approximate_algorithm)
    3) Повний перебір (exhaustive_search) для матриць розміром ≤ 3×3
    """
    print("Введіть спосіб введення матриці:")
    print("1 - Ручне введення")
    print("2 - Випадкова генерація")
    print("3 - Зчитування з файлу input.txt")
    choice = logged_input(PROMPT_INPUT).strip()

    input_methods = {
        "1": _input_manual,
        "2": _input_random,
        "3": _input_from_file,
    }

    if choice not in input_methods:
        print("Невірний вибір способу введення.")
        return

    result = input_methods[choice]()
    if result is None:
        return
    m, n, _, matrix = result

    # Запуск жадібного та наближеного алгоритмів
    greedy_algorithm(
        matrix,
        m,
        n,
        max_iterations=1000,
        stability_threshold=50,
        local_search_type="1",
    )
    approximate_algorithm(
        matrix,
        m,
        n,
        max_iterations=1000,
        stability_threshold=50,
        local_search_type="1",
    )

    # Якщо матриця маленька, запускаємо повний перебір
    if m * n > 9:
        print("Розмір матриці перевищує 3×3, розв'язання повним перебором неможливе.")
    else:
        exhaustive_result = exhaustive_search(matrix, m, n)
        if exhaustive_result:
            print("Матриця розподілу:")
            for row in exhaustive_result["matrix"]:
                print(" ".join(str(cell) for cell in row))
            print(f"Час виконання: {exhaustive_result['execution_time']:.4f} секунд")
            print(
                "Загальна вартість для кожного забудовника: "
                f"{exhaustive_result['total_costs']}"
            )
            print(f"Максимальне відхилення: {exhaustive_result['max_deviation']}")


def run_experiments() -> None:
    """
    Виконує обраний експеримент та будує графіки.

    Експерименти:
        1) Вплив кількості ітерацій наближеного алгоритму
        2) Вплив верхньої межі вартості на ефективність
        3) Залежність часу виконання від розмірності
        4) Залежність точності від розмірності

    Графіки зберігаються у теці 'experiment_plots'.
    """
    print("Оберіть експеримент:")
    print(
        "1 - Вплив кількості ітерацій наближеного двоетапного алгоритму "
        "на точність і час"
    )
    print("2 - Вплив верхньої межі вартості ділянки на ефективність алгоритмів")
    print("3 - Залежність часу виконання від розмірності")
    print("4 - Залежність точності виконання від розмірності")
    choice = logged_input(PROMPT_INPUT).strip()

    if not os.path.exists("experiment_plots"):
        os.makedirs("experiment_plots")

    experiment_mapping = {
        "1": (
            experiments.experiment_3_4_1,
            plotters.plot_iterations_vs_metric,
            ("experiment_plots/experiment_3_4_1",),
        ),
        "2": (
            experiments.experiment_3_4_2,
            plotters.plot_c_vs_metrics,
            (),
        ),
        "3": (
            experiments.experiment_3_4_3_1,
            plotters.plot_sizes_vs_times,
            (),
        ),
        "4": (
            experiments.experiment_3_4_3_2,
            plotters.plot_sizes_vs_deviation,
            (),
        ),
    }

    if choice not in experiment_mapping:
        print("Невірний вибір експерименту.")
        return

    func, plot_func, extra_args = experiment_mapping[choice]
    result = func()

    if choice == "1":
        iters, deviations, times = result
        plot_func(iters, deviations, times, extra_args[0])
    elif choice == "2":
        c_values, g_dev, a_dev, e_dev, g_time, a_time, e_time = result
        plot_func(c_values, g_dev, a_dev, e_dev, g_time, a_time, e_time)
    elif choice == "3":
        sizes, g_times, a_times = result
        plot_func(sizes, g_times, a_times)
    else:  # choice == "4"
        sizes, g_devs, a_devs = result
        plot_func(sizes, g_devs, a_devs)

    print("Експеримент завершено. Графіки збережено у папці 'experiment_plots'.")


def _process_main_choice(choice: str) -> bool:
    """
    Обробляє вибір користувача у головному меню.

    Args:
        choice: Строка з вибором ("1", "2" або "0").

    Returns:
        False — якщо потрібно завершити програму, True — щоб продовжити.
    """
    if choice == "1":
        solve_task()
    elif choice == "2":
        run_experiments()
    elif choice == "0":
        print("Вихід з програми.")
        return False
    else:
        print("Невірний вибір, спробуйте ще раз.")
    return True


def main() -> None:
    """
    Головна функція програми.

    Перенаправляє stdout/stderr у лог-файл та запускає цикл меню:
        1) Розв'язати задачу
        2) Провести експерименти
        0) Вийти
    """
    sys.stdout = Logger("result_output.txt")
    sys.stderr = sys.stdout

    try:
        continue_running = True
        while continue_running:
            print("\nВиберіть дію:")
            print("1 - Розв'язати задачу")
            print("2 - Провести експерименти")
            print("0 - Вийти")
            user_choice = logged_input(PROMPT_INPUT).strip()
            continue_running = _process_main_choice(user_choice)
    finally:
        sys.stdout.close()


if __name__ == "__main__":
    main()
