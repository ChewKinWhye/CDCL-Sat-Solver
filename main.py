from dpll import DPLL
from cdcl import CDCL
import time
import csv
from utils import read_data, generate_test_cases, obtain_labels, calc_accuracy
import os

base_dir = "data"

def test_DPLL(num_test_cases):
    row_solution = []
    for i in range(1, num_test_cases+1):
        print(i)
        file = f"test_case_{i}.cnf"
        _, _, cnf = read_data(file)
        prop = set()
        for row in cnf:
            for variable in row:
                if variable < 0:
                    prop.add(-variable)
                else:
                    prop.add(variable)
        start = time.perf_counter()
        sat = DPLL([cnf], [{}], [prop], 0)[0]
        time_taken = time.perf_counter() - start
        row_solution.append([i, sat, time_taken])
    with open('predictions.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in row_solution:
            spamwriter.writerow(row)


def test_CDCL(num_test_cases):
    row_solution = []
    for i in range(1, num_test_cases+1):
        file = f"test_case_{i}.cnf"
        _, _, cnf = read_data(file)
        prop = set()
        for row in cnf:
            for variable in row:
                if variable < 0:
                    prop.add(-variable)
                else:
                    prop.add(variable)
        start = time.perf_counter()
        print(f"Test Case: {i}")
        sat = CDCL([cnf], [{}], [prop], [[]])
        if sat == "UNSAT":
            sat = "False"
        else:
            sat = "True"
        time_taken = time.perf_counter() - start
        row_solution.append([i, sat, time_taken])
    with open(os.path.join(base_dir,'predictions.csv'), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in row_solution:
            spamwriter.writerow(row)


if __name__ == "__main__":
    num_test_cases = 1
    generate_test_cases(80, 300, 3, num_test_cases)
    print("Test cases generated")
    obtain_labels(num_test_cases)
    print("Labels obtained")
    test_CDCL(num_test_cases)
    print("Predictions obtained")
    accuracy, average_time_slower = calc_accuracy(num_test_cases)
    print(f"Accuracy = {accuracy * 100}%")
    print(f"Slower by {average_time_slower}s on average")
