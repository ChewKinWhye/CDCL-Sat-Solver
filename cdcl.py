import copy
import time


# O(1)
def pick_branching_variable_vsids(variables, level, vsids_scores_positive, vsids_scores_negative):
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
def pick_branching_variable(variables, level):
    return variables[level][0], 1

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
def backtrack(assignment, variables, level, branching_history, total_history):
    del assignment[level+1:]
    del variables[level+1:]
    del branching_history[level+1:]
    del total_history[level+1:]


def sanity_check(assignment, variables, branching_history, total_history, size):
    assert len(assignment) == size
    assert len(variables) == size
    assert len(branching_history) == size
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
    vsids_scores_positive = [i * 0.9 for i in vsids_scores_positive]
    vsids_scores_negative = [i * 0.9 for i in vsids_scores_negative]
    for literal in learnt:
        if literal > 0:
            vsids_scores_positive[abs(literal)] += 1
        else:
            vsids_scores_negative[abs(literal)] += 1
    return level, learnt


def conflict_analysis(conflict_clause, total_history, assignment, clauses, level,
                     vsids_scores_positive, vsids_scores_negative):
    if level == 0:
        return -1, None

    to_check = conflict_clause
    resolved = set()
    to_resolve = set()
    learnt_clause = set()

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
    for i in range(len(vsids_scores_positive)):
        vsids_scores_positive[i] = vsids_scores_positive[i] * 0.9
        vsids_scores_negative[i] = vsids_scores_negative[i] * 0.9
    for literal in learnt:
        if literal > 0:
            vsids_scores_positive[abs(literal)] += 1
        else:
            vsids_scores_negative[abs(literal)] += 1
    return level, learnt


def CDCL(clauses, assignment, variables, branching_history, total_history, single_UIP, VSIDS):
    # Initialize variables
    num_loop = 0
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
    while len(variables[level]) != 0:
        num_loop += 1
        # Pick variable
        # Run unit prop
        unsat_clause = unit_prop(clauses, assignment, variables, level, total_history)
        if unsat_clause is not None:
            if single_UIP:
                level, learnt = conflict_analysis_single_UIP(unsat_clause, total_history, assignment, clauses, level,
                                                                vsids_scores_positive, vsids_scores_negative)
            else:
                level, learnt = conflict_analysis(unsat_clause, total_history, assignment, clauses, level,
                                                    vsids_scores_positive, vsids_scores_negative)

            if level < 0:
                return False, num_loop, assignment[level]
            clauses.append(copy.deepcopy(learnt))
            backtrack(assignment, variables, level, branching_history, total_history)

        elif len(variables[level]) == 0:
            break
        else:
            if VSIDS:
                update_literal, update_value = pick_branching_variable_vsids(variables, level, vsids_scores_positive,
                                                                             vsids_scores_negative)
            else:
                update_literal, update_value = pick_branching_variable(variables, level)

            # Branch and expand search tree, go to next level
            assignment.append(copy.deepcopy(assignment[level]))
            variables.append(copy.deepcopy(variables[level]))
            branching_history.append(update_literal)
            total_history.append(copy.deepcopy(total_history[level]))
            level += 1
            # Assign Variable
            variable_assignment(assignment, variables, level, update_literal, update_value, None, total_history)
    return True, num_loop, assignment[level]
