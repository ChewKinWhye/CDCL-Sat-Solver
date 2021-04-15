import copy


def resolution(c1, c2, literal):
    c1.remove(literal)
    c2.remove(-literal)
    c1.extend(c2)
    return list(set(c1))


def variable_assignment(clauses, assignment, prop, level, update_literal, update_value, antecedent, history):
    new_clauses = []
    prop[level].remove(update_literal)
    assignment[level][update_literal] = (update_value, antecedent, level)
    history[level].append(abs(update_literal))
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


def unit_prop(clauses, assignment, prop, level, update_literal, update_value, history):
    to_update = True
    if update_literal is not None:
        variable_assignment(clauses, assignment, prop, level, update_literal, update_value, None, history)
    while to_update:
        to_update = False
        for idx, clause in enumerate(clauses[level]):
            if len(clause) == 0:
                return idx
            elif len(clause) == 1 and clause != "T":
                literal = list(clause)[0]
                if literal < 0:
                    update_value = 0
                    update_literal = -literal
                else:
                    update_value = 1
                    update_literal = literal
                variable_assignment(clauses, assignment, prop, level, update_literal, update_value, idx, history)
                to_update = True
                break
    return "SAT"


def next_recent_assigned(clause, assignment, level, history):
    for v in reversed(history[level]):
        if v in clause or -v in clause:
            return v, [x for x in clause if abs(x) != abs(v)]


def conflict_analysis_new(clauses, assignment, prop, level, unsat_clause, history):
    """
    Analyze the most recent conflict and learn a new clause from the conflict.
    - Find the cut in the implication graph that led to the conflict
    - Derive a new clause which is the negation of the assignments that led to the conflict
    Returns a decision level to be backtracked to.
    :param conf_cls: (set of int) the clause that introduces the conflict
    :return: ({int} level to backtrack to, {set(int)} clause learnt)
    """
    initial_level = level

    pool_lits = copy.deepcopy(clauses[0][unsat_clause])
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

        last_assigned, others = next_recent_assigned(curr_level_lits,  assignment, level, history)

        done_lits.add(abs(last_assigned))
        curr_level_lits = set(others)

        pool_clause = assignment[level][abs(last_assigned)][1]
        pool_lits = [
            l for l in copy.deepcopy(clauses[0][pool_clause]) if abs(l) not in done_lits
        ] if pool_clause is not None else []

    learnt = frozenset([l for l in curr_level_lits.union(prev_level_lits)])
    if prev_level_lits:
        level = max([assignment[level][abs(x)][2] for x in prev_level_lits])
    else:
        level = level - 1
    print(f"Level Change: {initial_level - level}")

    return level, learnt


# Need to check if assignment is list of list or list of set
# Need to check if I need to loop through the levels

    # print("???")

# def conflict_analysis_new(clauses, assignment, prop, level, unsat_clause, history):
#     # Check if it should be level 0 or level 1
#     initial_level = level
#     # Obtain conflict clause
#     pool_lits  = copy.deepcopy(clauses[0][unsat_clause])
#     # print(f"Unsat Clause: {unsat_clause}")
#     done_lits = set()
#     curr_level_lits = set()
#     prev_level_lits = set()
#     while True:
#         for lit in pool_lits:
#             # Check what level this lit was assigned at
#             if assignment[level][abs(lit)][2] == level:
#                 curr_level_lits.add(lit)
#             else:
#                 prev_level_lits.add(lit)
#         if len(curr_level_lits) == 1:
#             break
#         last_assigned, others = next_recent_assigned(curr_level_lits, assignment, level, history)
#         done_lits.add(abs(last_assigned))
#         curr_level_lits = set(others)
#         pool_clause = assignment[level][abs(last_assigned)][1]
#         if pool_clause is None:
#             pool_lits = []
#         else:
#             pool_clause = copy.deepcopy(clauses[0][pool_clause])
#             pool_lits = [l for l in pool_clause if abs(l) not in done_lits]
#
#     learnt = frozenset([l for l in curr_level_lits.union(prev_level_lits)])
#     if prev_level_lits:
#         level = max([assignment[level][abs(x)][2] for x in prev_level_lits])
#     else:
#         level = level - 1
#     # print(f"Level Change: {initial_level - level}")
#     return level, learnt


def pick_branching_variable(clauses, assignment, prop, level, updates, history):
    if len(assignment) > level:
        if updates[level][1] == 0:
            update_clause, update_value = updates[level][0], 1
        else:
            update_clause, update_value = "UNSAT", "UNSAT"
        back_prop(clauses, assignment, prop, level, updates, history)
        return update_clause, update_value
    else:
        literal = list(prop[level-1])[0]
        if literal < 0:
            return -literal, 0
        else:
            return literal, 0

def back_prop(clauses, assignment, prop, level, updates, history):
    del clauses[level:]
    del assignment[level:]
    del prop[level:]
    del updates[level:]
    del history[level:]


# clauses is a list of lists of set
# assignment is a list of dict
# prop is a list of sets


def CDCL(clauses, assignment, prop, updates, history):
    # Start from 0 level
    level = 0
    # unit_prop updates clauses, assignment and prop at the level
    if unit_prop(clauses, assignment, prop, level, None, None, history) == "UNSAT":
        return "UNSAT"
    while len(prop[level]) != 0:
        level += 1
        update_literal, update_value = pick_branching_variable(clauses, assignment, prop, level, updates, history)
        if update_literal == "UNSAT":
            if level == 1:
                return "UNSAT"
            level -= 2
            continue
        clauses.append(copy.deepcopy(clauses[level-1]))
        assignment.append(copy.deepcopy(assignment[level-1]))
        prop.append(copy.deepcopy(prop[level-1]))
        updates.append([update_literal, update_value])
        history.append(copy.deepcopy(history[level-1]))
        # print(f"Level: {level}")
        # print(f"Updates: {update_literal}, {update_value}")
        # print(f"Clauses {clauses}")
        # print(f"Propositions: {prop}")
        # print(f"Assignments: {assignment}")
        sat = unit_prop(clauses, assignment, prop, level, update_literal, update_value, history)
        if sat != "SAT":
            # level, learnt = conflict_analysis_new(clauses, assignment, prop, level, sat, history)
            level -= 1
    return "SAT"
