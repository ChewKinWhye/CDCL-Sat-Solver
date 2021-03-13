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
  DIMACS = ""
  DIMACS += "c A .cnf test case file.\n"
  DIMACS += f"p cnf {N} {L}\n"
  clauses = [i for i in range(1, N + 1)]
  for i in range (L):
    clause_variables = random.sample(clauses, K)
    for variable in clause_variables:
      if random.random() > 0.5:
        DIMACS += f"{variable} "
      else:
        DIMACS += f"{-variable} "
    DIMACS += "0\n"
  return DIMACS

def generate_test_cases(N, L, K, num_test_cases):
    for i in range(num_test_cases):
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
    with open(os.path.join(base_dir, file_path)) as f:
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
                cnf.append(content_int)
    return num_variables, num_clauses, cnf


def obtain_labels(num_test_cases):
    row_solution = []
    for i in range(1, num_test_cases+1):
        s = Solver()
        file = f"test_case_{i}.cnf"
        _, _, cnf = read_data(file)
        for row in cnf:
            s.add_clause(row)
        start = time.perf_counter()
        sat, _ = s.solve()
        time_taken = time.perf_counter() - start
        row_solution.append([i, sat, time_taken])
    with open(os.path.join(base_dir, 'labels.csv'), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in row_solution:
            spamwriter.writerow(row)







