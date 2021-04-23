from cdcl import CDCL
import time
import csv
from utils import read_data, generate_test_cases, obtain_labels, calc_accuracy
import os

base_dir = "data"
single_UIP = False
# branching_heuristic ["VSIDS", "random", "2-clause"]
branching_heuristic = "VSIDS"

def test_einstein():
    file = "einstein_puzzle.cnf"
    # Read the data from einstein.cnf to obtain the CNF formula
    _, _, cnf = read_data(file)

    start = time.perf_counter()
    # Run solver on eintein.cf 200 times
    for i in range(200):
        sat, assignment = CDCL(cnf, single_UIP, branching_heuristic)
    time_taken = time.perf_counter() - start
    # Print average time taken
    print(sat, time_taken/200)

    # Obtain reference to decode assignment
    reference = [""]
    with open("reference.txt", "r") as f:
        for x in f:
            if len(x) > 2:
                reference.append(x[6:-1])
    # Print out the decoded assignment
    for idx in assignment:
        if assignment[idx][0] == 1:
            print(reference[int(idx)])


def test_solver():
    num_test_cases = 50
    # Generate Test cases
    generate_test_cases(100, 450, 3, num_test_cases)
    # Obtain labels from online solver
    obtain_labels(num_test_cases)

    row_solution = []
    time_taken_total = 0
    # Loop through test cases
    for i in range(1, num_test_cases + 1):
        file = os.path.join(base_dir, f"test_case_{i}.cnf")
        _, _, cnf = read_data(file)
        start = time.perf_counter()
        # Run our solver
        sat, _ = CDCL(cnf, single_UIP, branching_heuristic)
        time_taken = time.perf_counter() - start
        time_taken_total += time_taken
        # Store solution
        row_solution.append([i, sat, time_taken])
        print(time_taken)

    # Save solution
    with open(os.path.join(base_dir, 'predictions.csv'), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in row_solution:
            spamwriter.writerow(row)
    # Print metrics
    accuracy, average_time_slower = calc_accuracy(num_test_cases)
    print(f"Accuracy = {accuracy * 100}%")
    print(f"Average Time Taken: {time_taken_total / num_test_cases}")
    print(f"Slower by {average_time_slower}s on average")


if __name__ == "__main__":
    # Run the solver on einstein puzzle
    # test_einstein()
    # Run the solver on randomly generate test cases
    test_solver()
