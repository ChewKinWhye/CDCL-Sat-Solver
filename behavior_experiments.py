from utils import generate_test_cases, obtain_labels
import math
from os.path import join
import pickle
from matplotlib import pyplot as plt
base_dir = "data"


if __name__ == "__main__":
    # Fix number of variables at 150 and k at 3
    n = 150
    k = 4
    num_test_cases = 50
    r_values = [x * 0.2 for x in range(41, 51)]
    results = []
    save_directory = join("experiment_results", f"k={k}")

    for r in r_values:
        num_clauses = math.ceil(r*n)
        generate_test_cases(n, num_clauses, k, num_test_cases)
        num_sat = obtain_labels(num_test_cases)
        sat_probability = num_sat/num_test_cases
        results.append(sat_probability)
        print(sat_probability)
    with open(join(save_directory, "raw"), "wb") as f:
        pickle.dump(results, f)
    plt.plot(r_values, results)
    plt.xlabel("r")
    plt.ylabel("Sat Probability")
    plt.show()
    plt.savefig(join(save_directory, "plot"))
