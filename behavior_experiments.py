from utils import generate_test_cases, obtain_labels
import math
from os.path import join
import pickle
from matplotlib import pyplot as plt
base_dir = "data"


'''
In this code, we run experiments to see how the value of r and k
impacts the probability that the CNF formula is satisfiable
'''
if __name__ == "__main__":
    # Fix number of variables at 150, k at 3, and number of test cases at 50
    n = 150
    k = 4
    num_test_cases = 50
    save_directory = join("experiment_results", f"k={k}")
    # Obtain the values for r
    r_values = [x * 0.2 for x in range(1, 51)]
    results = []

    # Loop through the values of r
    for r in r_values:
        # Calculate the number of clauses given by L = r * n
        num_clauses = math.ceil(r*n)
        # Generate the test cases. The test cases are stored in the data folder
        generate_test_cases(n, num_clauses, k, num_test_cases)
        # Obtain the labels. The function loops through the test cases in the data folder and runs the sat solver
        num_sat = obtain_labels(num_test_cases)
        # Calculate the Sat Probability and add it to the results
        sat_probability = num_sat/num_test_cases
        results.append(sat_probability)
    # Save the results
    with open(join(save_directory, "raw"), "wb") as f:
        pickle.dump(results, f)
    # Plot the results
    plt.plot(r_values, results)
    plt.xlabel("r")
    plt.ylabel("Sat Probability")
    plt.show()
    # Save the plot
    plt.savefig(join(save_directory, "plot"))
