import copy
import time


def pick_branching_variable(variables, level, total_branching_choices):
    total_branching_choices[level].add((variables[level][0], 1))
    return variables[level][0], 1



def variable_assignment(clauses, assignment, variables, level, update_literal, update_value, antecedent_idx, total_history):
    variables[level].remove(update_literal)
    assignment[level][update_literal] = (update_value, antecedent_idx, level)
    total_history[level].append(update_literal)
    new_clauses = []
    for clause in clauses[level]:
        if clause == "T":
            new_clauses.append("T")

        elif update_literal in clause:
            if update_value == 1:
                new_clauses.append("T")
            else:
                temp = copy.deepcopy(clause)
                temp.remove(update_literal)
                new_clauses.append(temp)
        elif -update_literal in clause:
            if update_value == 0:
                new_clauses.append("T")
            else:
                temp = copy.deepcopy(clause)
                temp.remove(-update_literal)
                new_clauses.append(temp)
        else:
            new_clauses.append(copy.deepcopy(clause))
    clauses[level] = copy.deepcopy(new_clauses)


def unit_prop(clauses, assignment, variables, level, total_history):
    while True:
        to_update = {}
        for idx, clause in enumerate(clauses[level]):
            if len(clause) == 0:
                return clauses[0][idx]
            elif len(clause) == 1 and clause != "T":
                literal = list(clause)[0]
                update_value = 0 if literal < 0 else 1
                update_literal = abs(literal)
                if update_literal not in to_update:
                    to_update[update_literal] = (update_value, idx)
        if len(to_update) == 0:
            break
        for update in to_update:
            variable_assignment(clauses, assignment, variables, level, update, to_update[update][0], to_update[update][1], total_history)
    return None


def backtrack(clauses, assignment, variables, level, branching_history, total_branching_choices, total_history):
    del clauses[level+1:]
    del assignment[level+1:]
    del variables[level+1:]
    del branching_history[level+1:]
    del total_history[level+1:]
    del total_branching_choices[level + 1:]


def sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, size):
    assert len(clauses) == size
    assert len(assignment) == size
    assert len(variables) == size
    assert len(branching_history) == size
    assert len(total_history) == size
    assert len(total_branching_choices) == size


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
            pool_clause = clauses[0][assignment[level][abs(last_assigned)][1]]
            pool_lits = [l for l in pool_clause if abs(l) not in done_lits]

    learnt = [l for l in curr_level_lits.union(prev_level_lits)]
    if prev_level_lits:
        level = max([assignment[level][abs(x)][2] for x in prev_level_lits])
    else:
        level = level - 1
    return level, learnt


def CDCL(clauses, assignment, variables, branching_history, total_history, total_branching_choices):
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
            for i in range(level + 1):
                learnt_copy = []
                for literal in learnt:
                    if abs(literal) in assignment[i]:
                        if literal < 0:
                            assert assignment[i][abs(literal)][0] == 1
                        else:
                            assert assignment[i][abs(literal)][0] == 0
                    else:
                        learnt_copy.append(literal)
                clauses[i].append(copy.deepcopy(learnt_copy))

            backtrack(clauses, assignment, variables, level, branching_history, total_history, total_branching_choices)
            sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices,
                         level + 1)
        elif len(variables[level]) == 0:
            break
        else:
            sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level+1)
            update_literal, update_value = pick_branching_variable(variables, level, total_branching_choices)
            sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level + 1)

            # Branch and expand search tree, go to next level
            clauses.append(copy.deepcopy(clauses[level]))
            assignment.append(copy.deepcopy(assignment[level]))
            variables.append(copy.deepcopy(variables[level]))
            branching_history.append(update_literal)
            total_history.append(copy.deepcopy(total_history[level]))
            total_branching_choices.append(copy.deepcopy(total_branching_choices[level]))
            level += 1

            # Run Unit Prop
            sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level + 1)
            variable_assignment(clauses, assignment, variables, level, update_literal, update_value, None, total_history)
            sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level+1)

    return True
