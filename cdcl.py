import copy
import time

# O(1)
def pick_branching_variable(variables, level):
    return variables[level][0], 1

# O(1)
def variable_assignment(assignment, variables, level, update_literal, update_value, antecedent_idx, total_history):
    variables[level].remove(update_literal)
    assignment[level][update_literal] = (update_value, antecedent_idx, level)
    total_history[level].append(update_literal)

# O(1)
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


def next_recent_assigned(clause, level_history):
    for v in reversed(level_history):
        if v in clause or -v in clause:
            return v, [x for x in clause if abs(x) != abs(v)]


def conflict_analyze(conf_cls, total_history, assignment, clauses, level):
    if level == 0:
        return -1, None

    pool_lits = conf_cls
    done_lits = set()
    curr_level_lits = set()
    prev_level_lits = set()

    while True:
        for lit in pool_lits:
            if assignment[level][abs(lit)][2] == level:
                curr_level_lits.add(lit)
            else:
                prev_level_lits.add(lit)

        if len(curr_level_lits) == 1:
            break

        last_assigned, others = next_recent_assigned(curr_level_lits, total_history[level])

        done_lits.add(abs(last_assigned))
        curr_level_lits = set(others)

        if assignment[level][abs(last_assigned)][1] is None:
            pool_lits = []
        else:
            pool_clause = clauses[assignment[level][abs(last_assigned)][1]]
            pool_lits = [l for l in pool_clause if abs(l) not in done_lits]

    learnt = [l for l in curr_level_lits.union(prev_level_lits)]
    if prev_level_lits:
        level = max([assignment[level][abs(x)][2] for x in prev_level_lits])
    else:
        level = level - 1
    return level, learnt


def CDCL(clauses, assignment, variables, branching_history, total_history):
    # Initialize variables
    level = 0

    # Backtrack seach loop
    while len(variables[level]) != 0:
        # Pick variable
        # Run unit prop
        unsat_clause = unit_prop(clauses, assignment, variables, level, total_history)
        if unsat_clause is not None:
            level, learnt = conflict_analyze(unsat_clause, total_history, assignment, clauses, level)
            if level < 0:
                return False
            clauses.add(copy.deepcopy(learnt))

            backtrack(assignment, variables, level, branching_history, total_history)
        elif len(variables[level]) == 0:
            break
        else:
            update_literal, update_value = pick_branching_variable(variables, level)

            # Branch and expand search tree, go to next level
            assignment.append(copy.deepcopy(assignment[level]))
            variables.append(copy.deepcopy(variables[level]))
            branching_history.append(update_literal)
            total_history.append(copy.deepcopy(total_history[level]))
            level += 1

            # Run Unit Prop
            variable_assignment(assignment, variables, level, update_literal, update_value, None, total_history)

    return True
