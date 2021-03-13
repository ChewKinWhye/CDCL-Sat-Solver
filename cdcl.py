import copy

def resolution(c1, c2):
    if len(c1) > len(c2):
        c1, c2 = c2, c1
    for l in c1:
        if -l in c2:
            c1.pop(l)
            c2.pop(-l)
            return copy.deepcopy(c1.union(c2))
    return set()


def variable_assignment(clauses, assignment, prop, level, update_literal, update_value):
    new_clauses = []
    prop[level].remove(update_literal)
    assignment[level][update_literal][0] = update_value
    for clause in clauses[level]:
        if update_literal in clause:
            if update_value == 1:
                continue
            else:
                temp = copy.deepcopy(clause)
                temp.remove(update_literal)
                new_clauses.append(temp)
                for literal in temp:
                    if literal < 0:
                        assignment[level][-literal][1].append(update_literal)
                    else:
                        assignment[level][literal][1].append(update_literal)
        elif -update_literal in clause:
            if update_value == 0:
                continue
            else:
                temp = copy.deepcopy(clause)
                temp.remove(-update_literal)
                new_clauses.append(temp)
                for literal in temp:
                    if literal < 0:
                        assignment[level][-literal][1].append(update_literal)
                    else:
                        assignment[level][literal][1].append(update_literal)
        else:
            new_clauses.append(copy.deepcopy(clause))
    clauses[level] = copy.deepcopy(new_clauses)


def unit_prop(clauses, assignment, prop, level, update_literal, update_value):
    to_update = True
    while to_update:
        to_update = False
        if update_literal is not None:
            variable_assignment(clauses, assignment, prop, level, update_literal, update_value)
        for clause in clauses[level]:
            if len(clause) == 0:
                return "UNSAT"
            elif len(clause) == 1:
                literal = list(clause)[0]
                if literal < 0:
                    update_value = 0
                    update_literal = -literal
                else:
                    update_value = 1
                    update_literal = literal
                to_update = True
                break
    return "SAT"


def conflict_analysis(clauses, assignment, prop, level):
    # Find UNSAT clause
    # Build Implication Graph
    # Clause Learning
    # Add clause
    # Find level
    return 1


def pick_branching_variable(clauses, assignment, prop, level, updates):
    if len(assignment) > level:
        if updates[level][1] == 0:
            update_clause, update_value = updates[level][0], 1
        else:
            update_clause, update_value = "UNSAT", "UNSAT"
        back_prop(clauses, assignment, prop, level, updates)
        return update_clause, update_value
    else:
        literal = list(prop[level-1])[0]
        if literal < 0:
            return -literal, 0
        else:
            return literal, 0

def back_prop(clauses, assignment, prop, level, updates):
    del clauses[level:]
    del assignment[level:]
    del prop[level:]
    del updates[level:]


# clauses is a list of lists of set
# assignment is a list of dict
# prop is a list of sets


def CDCL(clauses, assignment, prop, updates):
    # Start from 0 level
    level = 0
    # unit_prop updates clauses, assignment and prop at the level
    if unit_prop(clauses, assignment, prop, level, None, None) == "UNSAT":
        return "UNSAT"
    while len(prop[level]) != 0:
        level += 1
        update_literal, update_value = pick_branching_variable(clauses, assignment, prop, level, updates)
        if update_literal == "UNSAT":
            if level == 1:
                return "UNSAT"
            level -= 2
            continue
        clauses.append(copy.deepcopy(clauses[level-1]))
        assignment.append(copy.deepcopy(assignment[level-1]))
        prop.append(copy.deepcopy(prop[level-1]))
        updates.append([update_literal, update_value])
        # print(f"Level: {level}")
        # print(f"Updates: {update_literal}, {update_value}")
        # print(f"Clauses {clauses}")
        # print(f"Propositions: {prop}")
        # print(f"Assignments: {assignment}")
        if unit_prop(clauses, assignment, prop, level, update_literal, update_value) == "UNSAT":
            # level = conflict_analysis(clauses, assignment, prop, level)
            level -= 1
    return "SAT"
