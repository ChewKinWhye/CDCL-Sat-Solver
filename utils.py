import random
from pycryptosat import Solver
import time
import csv
import os


base_dir = "data"

def calc_accuracy(num_test_cases):
    accuracy = 0
    time_difference = 0
    labels_list = []
    predictions_list = []
    with open(os.path.join(base_dir, 'labels.csv')) as labels:
        labels_reader = csv.reader(labels, delimiter=',')
        for row in labels_reader:
            labels_list.append(row[0].split(" "))

    with open(os.path.join(base_dir, 'predictions.csv')) as predictions:
        predictions_reader = csv.reader(predictions, delimiter=',')
        for row in predictions_reader:
            predictions_list.append(row[0].split(" "))
    for i in range(num_test_cases):
        assert labels_list[i][0] == predictions_list[i][0]
        if labels_list[i][1] == predictions_list[i][1]:
            accuracy += 1
            time_difference += float(predictions_list[i][2]) - float(labels_list[i][2])
    return accuracy / num_test_cases, time_difference / num_test_cases


def generate_test_case(N, L, K):
    # Initialize the test case header
    DIMACS = ""
    DIMACS += "c A .cnf test case file.\n"
    DIMACS += f"p cnf {N} {L}\n"
    clauses = [i for i in range(1, N + 1)]
    # Loop through the number of clauses
    for i in range (L):
        # For each clause, we sample K literals
        clause_variables = random.sample(clauses, K)
        # Loop through each variable
        for variable in clause_variables:
            # Randomly negate the variables with probability of 0.5
            if random.random() > 0.5:
                DIMACS += f"{variable} "
            else:
                DIMACS += f"{-variable} "
        DIMACS += "0\n"
    return DIMACS

def generate_test_cases(N, L, K, num_test_cases):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    # Loop through the number of test cases
    for i in range(num_test_cases):
        # Generate the test case and save it
        test_case = generate_test_case(N, L, K)
        with open(os.path.join(base_dir, f"test_case_{i+1}.cnf"), "w") as f:
            f.write(test_case)

def read_data(file_path):
    """
    This function takes in the file path of the CNF files
    And returns the relevant content
    """
    num_variables = 0
    num_clauses = 0
    cnf = []
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == 'c':
                continue
            if line[0] == 'p':
                content = line.split()
                num_variables = content[2]
                num_clauses = content[3]
            else:
                content = line.split()
                content_int = [int(i) for i in content[:-1]]
                cnf.append(set(content_int))
    return num_variables, num_clauses, cnf


def obtain_labels(num_test_cases):
    row_solution = []
    num_sat = 0
    # Loop through the test cases
    for i in range(1, num_test_cases+1):
        # Initialize the solver
        s = Solver()
        file = os.path.join(base_dir, f"test_case_{i}.cnf")
        # Obtain the CNF formula of the test case
        _, _, cnf = read_data(file)
        # Pass the CNF into the solver
        for row in cnf:
            s.add_clause(row)
        start = time.perf_counter()
        # Solve the CNF
        sat, _ = s.solve()
        # Obtain the number of satisfiable formulas
        if sat:
            num_sat += 1
        # Record time taken for single test case
        time_taken = time.perf_counter() - start
        # Store the results
        row_solution.append([i, sat, time_taken])
    # Save the results
    with open(os.path.join(base_dir, 'labels.csv'), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in row_solution:
            spamwriter.writerow(row)
    return num_sat






