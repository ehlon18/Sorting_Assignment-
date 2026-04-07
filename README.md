# Sorting Assignment

## Students Names
- Eylon Horev
- Aharon Madar

## Selected Algorithms
- 1. Bubble Sort
- 2. Selection Sort
- 3. Insertion Sort
- 4. Merge Sort
- 5. Quick Sort 

## How To Run
Install dependency:

```bash
pip install matplotlib
```

Run experiment example:

```bash
python run_experiments.py -a 1 4 5 -s 100 500 1000 5000 -e 1 -r 20
```

CLI options:
- `-a` algorithms to compare (IDs 1..5)
- `-s` array sizes
- `-e` nearly sorted noise experiment (`1` = 5%, `2` = 20%)
- `-r` repetitions per size

Note that for the O(n^2) algorithms, we limited the array size they can accept to 50,000, so as not to cause very long runtimes.

## Figures

### result1.png (Random Arrays)
This plot compares average running time (with standard deviation error bars) on random integer arrays. Slower `O(n^2)` methods should grow much faster than `O(n log n)` methods as size increases.

### result2.png (Nearly Sorted Arrays)
This plot shows behavior on nearly sorted data. Algorithms that benefit from partial order can improve significantly, while others may see smaller improvements depending on pivot behavior and implementation details. quick sort, for example, actully can preform worse in this case.
