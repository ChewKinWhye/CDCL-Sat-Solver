# from online_copy_refactored import Solver
from online_copy import Solver

import time
import csv
from utils import read_data, generate_test_cases, obtain_labels, calc_accuracy
import os

base_dir = "data"


def test_online_generated(num_test_cases):
    generate_test_cases(100, 450, 3, num_test_cases)
    obtain_labels(num_test_cases)
    row_solution = []
    total_loops = 0
    time_taken_total = 0
    for i in range(1, num_test_cases+1):
        file = os.path.join(base_dir, f"test_case_{i}.cnf")
        print("1")
        solver = Solver(file)
        start = time.perf_counter()

        sat, num_loop = solver.solve()
        time_taken = time.perf_counter() - start
        row_solution.append([i, sat, time_taken])
        total_loops += num_loop
        time_taken_total += time_taken
    print(f"Average Number of Loops: {total_loops / num_test_cases}")
    print(f"Average Time Taken: {time_taken_total / num_test_cases}")
    with open(os.path.join(base_dir,'predictions.csv'), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in row_solution:
            spamwriter.writerow(row)


def test_einstein():
    file = os.path.join("einstein.cnf")
    solver = Solver(file)
    start = time.perf_counter()
    sat = solver.solve()
    time_taken = time.perf_counter() - start
    print(sat, time_taken)


if __name__ == "__main__":
    num_test_cases = 50
    test_einstein()
    test_online_generated(num_test_cases)
    print("Predictions obtained")
    accuracy, average_time_slower = calc_accuracy(num_test_cases)
    print(f"Accuracy = {accuracy * 100}%")
    print(f"Slower by {average_time_slower}s on average")
