import copy
import time
import random


# O(1)

def pick_branching_variable_vsids(variables, level, vsids_scores_positive, vsids_scores_negative, most_recent_unsat):
    max_score = float("-inf")
    variable_choice = None
    assignment = None
    if most_recent_unsat is not None:
        for variable in most_recent_unsat:
            if variable not in variables[level]:
                continue
            if vsids_scores_positive[variable] > max_score:
                max_score = vsids_scores_positive[variable]
                variable_choice = abs(variable)
                assignment = 1
            if vsids_scores_negative[variable] > max_score:
                max_score = vsids_scores_positive[variable]
                variable_choice = abs(variable)
                assignment = 0

    if variable_choice is None:
        max_score = float("-inf")
        variable_choice = None
        assignment = None
        for variable in variables[level]:
            if vsids_scores_positive[variable] > max_score:
                max_score = vsids_scores_positive[variable]
                variable_choice = variable
                assignment = 1
            if vsids_scores_negative[variable] > max_score:
                max_score = vsids_scores_positive[variable]
                variable_choice = variable
                assignment = 0

    return variable_choice, assignment


# O(1)
def pick_branching_variable_random(variables, level):
    return random.sample(variables[level], 1)[0], 1


def pick_branching_variable_2_clause(variables, level, clauses):
    # Initialize number of occurrences
    occurrences = {}
    for variable in variables[level]:
        occurrences[variable] = 0
    # Increment occurrences
    for clause in clauses:
        for literal in clause:
            if abs(literal) in variables[level]:
                occurrences[abs(literal)] += 1
    max_value = float("-inf")
    max_literal = None
    for key in occurrences:
        if occurrences[key] > max_value:
            max_literal = key
            max_value = occurrences[key]
    return max_literal, 1


# O(1)
def variable_assignment(assignment, variables, level, update_literal, update_value, antecedent_idx, total_history):
    variables[level].remove(update_literal)
    assignment[level][update_literal] = (update_value, antecedent_idx, level)
    total_history[level].append(update_literal)

# O(3)
def evaluate_clause(clause, assignment, level):
    count_false = 0
    unassigned = None
    for literal in clause:
        if abs(literal) in assignment[level]:
            if literal > 0 and assignment[level][abs(literal)][0] == 1 or literal < 0 and assignment[level][abs(literal)][0] == 0:
                return True
            else:
                count_false += 1
        else:
            unassigned = literal
    if count_false == len(clause):
        return False
    elif count_false + 1 == len(clause):
        return unassigned
    else:
        return None

def unit_prop(clauses, assignment, variables, level, total_history):
    while True:
        to_update = {}
        for idx, clause in enumerate(clauses):
            evaluation = evaluate_clause(clause, assignment, level)
            if evaluation is True:
                continue
            elif evaluation is False:
                return copy.deepcopy(clauses[idx])

            elif evaluation is not None:
                update_value = 0 if evaluation < 0 else 1
                update_literal = abs(evaluation)
                if update_literal not in to_update:
                    to_update[update_literal] = (update_value, idx)
        if len(to_update) == 0:
            break
        for update in to_update:
            variable_assignment(assignment, variables, level, update, to_update[update][0], to_update[update][1], total_history)
    return None


# O(1)
def backtrack(assignment, variables, level, total_history):
    del assignment[level+1:]
    del variables[level+1:]
    del total_history[level+1:]


def sanity_check(assignment, variables, total_history, size):
    assert len(assignment) == size
    assert len(variables) == size
    assert len(total_history) == size


def get_last_assigned(clause, level_history):
    for v in reversed(level_history):
        if v in clause:
            return v
        if -v in clause:
            return -v


def conflict_analysis_single_UIP(conflict_clause, total_history, assignment, clauses, level,
                                vsids_scores_positive, vsids_scores_negative):
    if level == 0:
        return -1, None

    to_check = conflict_clause
    resolved = set()
    to_resolve = set()
    learnt_clause = set()

    for literal in conflict_clause:
        if assignment[level][abs(literal)][1] is None:
            continue
        for antecedent_literal in clauses[assignment[level][abs(literal)][1]]:
            if antecedent_literal > 0:
                vsids_scores_positive[abs(antecedent_literal)] += 1
            else:
                vsids_scores_negative[abs(antecedent_literal)] += 1
    while True:
        for lit in to_check:
            if assignment[level][abs(lit)][2] == level:
                to_resolve.add(lit)
            else:
                learnt_clause.add(lit)

        if len(to_resolve) == 1:
            break

        last_assigned = get_last_assigned(to_resolve, total_history[level])

        resolved.add(abs(last_assigned))
        to_resolve.remove(last_assigned)

        if assignment[level][abs(last_assigned)][1] is None:
            to_check = []
        else:
            antecedent = clauses[assignment[level][abs(last_assigned)][1]]
            to_check = [l for l in antecedent if abs(l) not in resolved]

    learnt = [l for l in to_resolve.union(learnt_clause)]
    if learnt_clause:
        level = max([assignment[level][abs(x)][2] for x in learnt_clause])
    else:
        level = level - 1

    return level, learnt


def conflict_analysis(conflict_clause, total_history, assignment, clauses, level,
                     vsids_scores_positive, vsids_scores_negative):
    if level == 0:
        return -1, None

    to_check = conflict_clause
    resolved = set()
    to_resolve = set()
    learnt_clause = set()

    for literal in conflict_clause:
        if assignment[level][abs(literal)][1] is None:
            continue
        for antecedent_literal in clauses[assignment[level][abs(literal)][1]]:
            if antecedent_literal > 0:
                vsids_scores_positive[abs(antecedent_literal)] += 1
            else:
                vsids_scores_negative[abs(antecedent_literal)] += 1

    while True:
        for lit in to_check:
            if assignment[level][abs(lit)][1] is not None:
                to_resolve.add(lit)
            else:
                learnt_clause.add(lit)

        if len(to_resolve) == 0:
            break

        last_assigned = get_last_assigned(to_resolve, total_history[level])

        resolved.add(abs(last_assigned))
        to_resolve.remove(last_assigned)

        if assignment[level][abs(last_assigned)][1] is None:
            to_check = []
        else:
            antecedent = clauses[assignment[level][abs(last_assigned)][1]]
            to_check = [l for l in antecedent if abs(l) not in resolved]

    learnt = [l for l in to_resolve.union(learnt_clause)]
    if len(learnt_clause) == 1:
        level = level - 1
    else:
        max_level = float("-inf")
        second_max_level = float("-inf")
        for level in [assignment[level][abs(x)][2] for x in learnt_clause]:
            if level > max_level:
                second_max_level = max_level
                max_level = level
            elif level > second_max_level:
                second_max_level = level
        level = second_max_level
    return level, learnt


def CDCL(clauses, single_UIP, branching_heuristic):
    # Initialize variables
    variables = set()
    for row in clauses:
        for variable in row:
            variables.add(abs(variable))
    variables = [list(variables)]
    assignment, total_history = [{}], [[]]
    level = 0

    vsids_scores_positive = [0] * (len(variables[0]) + 1)
    vsids_scores_negative = [0] * (len(variables[0]) + 1)
    for clause in clauses:
        for literal in clause:
            if literal > 0:
                vsids_scores_positive[abs(literal)] += 1
            else:
                vsids_scores_negative[abs(literal)] += 1
    # Backtrack seach loop
    most_recent_unsat = None
    while len(variables[level]) != 0:
        # Pick variable
        # Run unit prop
        unsat_clause = unit_prop(clauses, assignment, variables, level, total_history)
        if unsat_clause is not None:
            most_recent_unsat = unsat_clause
            if single_UIP:
                level, learnt = conflict_analysis_single_UIP(unsat_clause, total_history, assignment, clauses, level,
                                                                vsids_scores_positive, vsids_scores_negative)
            else:
                level, learnt = conflict_analysis(unsat_clause, total_history, assignment, clauses, level,
                                                    vsids_scores_positive, vsids_scores_negative)

            if level < 0:
                return "False", None
            clauses.append(copy.deepcopy(learnt))
            backtrack(assignment, variables, level, total_history)

        elif len(variables[level]) == 0:
            break
        else:
            if branching_heuristic == "VSIDS":
                update_literal, update_value = pick_branching_variable_vsids(variables, level, vsids_scores_positive,
                                                                             vsids_scores_negative, most_recent_unsat)
            elif branching_heuristic == "random":
                update_literal, update_value = pick_branching_variable_random(variables, level)
            elif branching_heuristic == "2-clause":
                update_literal, update_value = pick_branching_variable_2_clause(variables, level, clauses)

            # Branch and expand search tree, go to next level
            assignment.append(copy.deepcopy(assignment[level]))
            variables.append(copy.deepcopy(variables[level]))
            total_history.append(copy.deepcopy(total_history[level]))
            level += 1
            # Assign Variable
            variable_assignment(assignment, variables, level, update_literal, update_value, None, total_history)
    return "True", assignment[level]
