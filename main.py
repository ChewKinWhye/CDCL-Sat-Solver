from cdcl import CDCL
import time
import csv
from utils import read_data, generate_test_cases, obtain_labels, calc_accuracy
import os

base_dir = "data"
single_UIP = False
VSIDS = True

def test_CDCL(num_test_cases):
    row_solution = []
    total_loops = 0
    time_taken_total = 0
    for i in range(1, num_test_cases+1):
        file = os.path.join(base_dir, f"test_case_{i}.cnf")
        _, _, cnf = read_data(file)
        prop = set()
        for row in cnf:
            for variable in row:
                prop.add(abs(variable))

        start = time.perf_counter()
        sat, num_loop = CDCL(cnf, [{}], [list(prop)], [-1], [[]], single_UIP, VSIDS)
        total_loops += num_loop
        if sat:
            sat = "True"
        else:
            sat = "False"
        time_taken = time.perf_counter() - start
        time_taken_total += time_taken
        row_solution.append([i, sat, time_taken])
        print(time_taken)
    print(f"Average Number of Loops: {total_loops/num_test_cases}")
    print(f"Average Time Taken: {time_taken_total / num_test_cases}")
    with open(os.path.join(base_dir,'predictions.csv'), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in row_solution:
            spamwriter.writerow(row)


def test_einstein():
    file = "einstein.cnf"
    _, _, cnf = read_data(file)
    prop = set()
    for row in cnf:
        for variable in row:
            prop.add(abs(variable))
    start = time.perf_counter()
    for i in range(200):
        sat = CDCL(cnf, [{}], [list(prop)], [-1], [[]], single_UIP, VSIDS)
        if sat:
            sat = "True"
        else:
            sat = "False"
    time_taken = time.perf_counter() - start
    print(sat, time_taken/200)


if __name__ == "__main__":
    test_einstein()
    num_test_cases = 50
    generate_test_cases(100, 450, 3, num_test_cases)
    print("Test cases generated")
    obtain_labels(num_test_cases)
    print("Labels obtained")
    test_CDCL(num_test_cases)
    print("Predictions obtained")
    accuracy, average_time_slower = calc_accuracy(num_test_cases)
    print(f"Accuracy = {accuracy * 100}%")
    print(f"Slower by {average_time_slower}s on average")
