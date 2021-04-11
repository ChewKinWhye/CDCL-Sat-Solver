import copy


def resolution(c1, c2, literal):
    c1.remove(literal)
    c2.remove(-literal)
    c1.extend(c2)
    return list(set(c1))


def variable_assignment(clauses, assignment, prop, level, update_literal, update_value, antecedent, history):
    new_clauses = []
    prop[level].remove(update_literal)
    assignment[level][update_literal] = (update_value, antecedent)
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


def conflict_analysis(clauses, assignment, prop, level, unsat_clause):
    unsat_clause = copy.deepcopy(clauses[0][unsat_clause])
    # print(f"Initial unsat clause: {unsat_clause} at level {level}")
    reset = True
    while reset:
        reset = False
        for literal in unsat_clause:
            variable = abs(literal)
            if variable in assignment[level]:
                antecedent = assignment[level][variable][1]
                if antecedent is None:
                    continue
                antecedent = copy.deepcopy(clauses[0][antecedent])
                unsat_clause = resolution(unsat_clause, antecedent, literal)
                reset = True
                break
    for literal in unsat_clause:
        if assignment[level][abs(literal)][1] is not None:
            print("ERROR")
    unsat_copy = copy.deepcopy(unsat_clause)
    assignment_level = 0
    for assignment_level in range(0, level):
        for literal in assignment[assignment_level]:
            if literal in unsat_copy:
                unsat_copy.remove(literal)
            elif -literal in unsat_copy:
                unsat_copy.remove(-literal)
            if len(unsat_copy) == 0:
                break
    # print(f"Learnt clause: {unsat_clause}, backtrack to level {assignment_level}")
    # print(assignment)

# Need to check if assignment is list of list or list of set
# Need to check if I need to loop through the levels
def next_recent_assigned(clause, assignment, level, history):
    # print(history[level])
    # print(clause)
    for v in reversed(history[level]):
        if v in clause or -v in clause:
            return v, [x for x in clause if abs(x) != abs(v)]
    # print("???")

def conflict_analysis_new(clauses, assignment, prop, level, unsat_clause, history):
    # Check if it should be level 0 or level 1
    print(f"Initial unsat level: {level}")
    if level == 0:
        return -1, 0
    # Obtain conflict clause
    unsat_clause = copy.deepcopy(clauses[0][unsat_clause])
    # print(f"Unsat Clause: {unsat_clause}")
    done_lits = set()
    curr_level_lits = set()
    prev_level_lits = set()
    while True:
        for lit in unsat_clause:
            # Check what level this lit was assigned at
            if abs(lit) in assignment[level]:
                curr_level_lits.add(lit)
            else:
                prev_level_lits.add(lit)
        if len(curr_level_lits) == 1:
            break
        last_assigned, others = next_recent_assigned(curr_level_lits, assignment, level, history)
        done_lits.add(abs(last_assigned))
        curr_level_lits = set(others)
        antecedent = assignment[level][abs(last_assigned)][1]
        if antecedent is None:
            unsat_clause = []
        else:
            pool_clause = copy.deepcopy(clauses[0][antecedent])
            unsat_clause = [l for l in pool_clause if abs(l) not in done_lits]

    learnt = frozenset([l for l in curr_level_lits.union(prev_level_lits)])
    if prev_level_lits:
        for max_level in range(level, -1, -1):
            for x in prev_level_lits:
                if x in assignment[max_level]:
                    level = max_level
    else:
        level = level - 1
    print(f"Backtrack level unsat level: {level}")
    return level, learnt


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
            _, _ = conflict_analysis_new(clauses, assignment, prop, level, sat, history)
            level -= 1
    return "SAT"
