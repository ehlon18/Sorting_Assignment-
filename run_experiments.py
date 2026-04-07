import argparse
import random
import statistics
import sys
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt


def bubble_sort(arr: List[int]) -> List[int]:
    n = len(arr)
    a = arr[:]
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def selection_sort(arr: List[int]) -> List[int]:
    a = arr[:]
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def insertion_sort(arr: List[int]) -> List[int]:
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr: List[int]) -> List[int]:
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    result: List[int] = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    if i < len(left):
        result.extend(left[i:])
    if j < len(right):
        result.extend(right[j:])
    return result


def quick_sort(arr: List[int]) -> List[int]:
    a = arr[:]
    _quick_sort_in_place(a, 0, len(a) - 1)
    return a


def _quick_sort_in_place(a: List[int], low: int, high: int) -> None:
    if low < high:
        p = _partition(a, low, high)
        _quick_sort_in_place(a, low, p - 1)
        _quick_sort_in_place(a, p + 1, high)


def _partition(a: List[int], low: int, high: int) -> int:
    pivot = a[high]
    i = low - 1
    for j in range(low, high):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[high] = a[high], a[i + 1]
    return i + 1


ALGORITHMS: Dict[int, Tuple[str, Callable[[List[int]], List[int]]]] = {
    1: ("Bubble Sort", bubble_sort),
    2: ("Selection Sort", selection_sort),
    3: ("Insertion Sort", insertion_sort),
    4: ("Merge Sort", merge_sort),
    5: ("Quick Sort", quick_sort),
}


@dataclass
class ExperimentResult:
    size: int
    mean_time: float
    std_time: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run sorting algorithm experiments and generate result plots."
    )
    parser.add_argument(
        "-a",
        "--algorithms",
        nargs="+",
        type=int,
        required=True,
        help="Algorithm IDs to compare (1..5).",
    )
    parser.add_argument(
        "-s",
        "--sizes",
        nargs="+",
        type=int,
        required=True,
        help="Array sizes for the experiments.",
    )
    parser.add_argument(
        "-e",
        "--experiment",
        type=int,
        default=1,
        choices=[1, 2],
        help="Nearly sorted noise setting: 1=5%% swaps, 2=20%% swaps.",
    )
    parser.add_argument(
        "-r",
        "--repetitions",
        type=int,
        default=10,
        help="Number of repetitions per size.",
    )
    parser.add_argument(
        "--max-quadratic-size",
        type=int,
        default=50000,
        help="Skip O(n^2) algorithms above this input size.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    invalid = [a for a in args.algorithms if a not in ALGORITHMS]
    if invalid:
        raise ValueError(f"Unknown algorithm id(s): {invalid}")
    if len(set(args.algorithms)) < 3:
        raise ValueError("Please provide at least 3 unique algorithm IDs.")
    if any(s <= 0 for s in args.sizes):
        raise ValueError("All array sizes must be positive.")
    if args.repetitions <= 0:
        raise ValueError("Repetitions must be positive.")


def is_quadratic(algorithm_id: int) -> bool:
    return algorithm_id in {1, 2, 3}


def make_random_array(size: int) -> List[int]:
    return [random.randint(0, 1_000_000) for _ in range(size)]


def make_nearly_sorted_array(size: int, noise_fraction: float) -> List[int]:
    arr = list(range(size))
    swaps = int(size * noise_fraction)
    for _ in range(swaps):
        i = random.randint(0, size - 1)
        j = random.randint(0, size - 1)
        arr[i], arr[j] = arr[j], arr[i]
    return arr


def time_algorithm(sort_fn: Callable[[List[int]], List[int]], arr: List[int]) -> float:
    start = time.perf_counter()
    result = sort_fn(arr)
    elapsed = time.perf_counter() - start
    if result != sorted(arr):
        raise RuntimeError("Sorting algorithm produced incorrect result.")
    return elapsed


def run_experiment(
    algorithms: Sequence[int],
    sizes: Sequence[int],
    repetitions: int,
    data_generator: Callable[[int], List[int]],
    max_quadratic_size: int,
) -> Dict[int, List[ExperimentResult]]:
    all_results: Dict[int, List[ExperimentResult]] = {algo_id: [] for algo_id in algorithms}
    for size in sizes:
        base_inputs = [data_generator(size) for _ in range(repetitions)]
        for algo_id in algorithms:
            algo_name, sort_fn = ALGORITHMS[algo_id]
            if is_quadratic(algo_id) and size > max_quadratic_size:
                print(
                    f"Skipping {algo_name} for size {size} "
                    f"(n^2 algorithm > max_quadratic_size={max_quadratic_size})."
                )
                continue
            times: List[float] = []
            for base in base_inputs:
                times.append(time_algorithm(sort_fn, base))
            all_results[algo_id].append(
                ExperimentResult(
                    size=size,
                    mean_time=statistics.mean(times),
                    std_time=statistics.stdev(times) if len(times) > 1 else 0.0,
                )
            )
    return all_results


def plot_results(
    results: Dict[int, List[ExperimentResult]],
    output_path: str,
    title: str,
) -> None:
    plt.figure(figsize=(10, 6))
    for algo_id, algo_results in results.items():
        if not algo_results:
            continue
        name = ALGORITHMS[algo_id][0]
        xs = [r.size for r in algo_results]
        ys = [r.mean_time for r in algo_results]
        yerr = [r.std_time for r in algo_results]
        plt.errorbar(xs, ys, yerr=yerr, marker="o", capsize=4, label=name)

    plt.xlabel("Array size (n)")
    plt.ylabel("Running time (seconds)")
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def print_table(results: Dict[int, List[ExperimentResult]], label: str) -> None:
    print(f"\n=== {label} ===")
    for algo_id, algo_results in results.items():
        print(f"\n{ALGORITHMS[algo_id][0]}")
        if not algo_results:
            print("  (no data)")
            continue
        for r in algo_results:
            print(f"  n={r.size:<8} mean={r.mean_time:.6f}s std={r.std_time:.6f}s")


def main() -> int:
    args = parse_args()
    try:
        validate_args(args)
    except ValueError as exc:
        print(f"Argument error: {exc}")
        return 1

    random.seed(args.seed)

    random_results = run_experiment(
        algorithms=args.algorithms,
        sizes=args.sizes,
        repetitions=args.repetitions,
        data_generator=make_random_array,
        max_quadratic_size=args.max_quadratic_size,
    )
    plot_results(
        random_results,
        output_path="result1.png",
        title="Sorting Algorithms on Random Arrays",
    )
    print_table(random_results, "Random Arrays (result1.png)")

    noise_fraction = 0.05 if args.experiment == 1 else 0.20
    nearly_sorted_results = run_experiment(
        algorithms=args.algorithms,
        sizes=args.sizes,
        repetitions=args.repetitions,
        data_generator=lambda n: make_nearly_sorted_array(n, noise_fraction),
        max_quadratic_size=args.max_quadratic_size,
    )
    plot_results(
        nearly_sorted_results,
        output_path="result2.png",
        title=f"Sorting Algorithms on Nearly Sorted Arrays ({int(noise_fraction * 100)}% noise)",
    )
    print_table(
        nearly_sorted_results,
        f"Nearly Sorted Arrays ({int(noise_fraction * 100)}% noise, result2.png)",
    )

    print("\nSaved plots: result1.png, result2.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
