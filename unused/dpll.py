import random


def variable_assignment(clauses, assignment, update_clause, level):
    new_clauses = []
    for clause in clauses[level]:
        if update_clause in clause:
            if assignment[level][update_clause] == 1:
                continue
            else:
                temp = clause.copy()
                temp.remove(update_clause)
                new_clauses.append(temp)
        elif -update_clause in clause:
            if assignment[level][update_clause] == 0:
                continue
            else:
                temp = clause.copy()
                temp.remove(-update_clause)
                new_clauses.append(temp)
        else:
            new_clauses.append(clause.copy())
    clauses[level] = new_clauses.copy()


def unit_prop(clauses, assignment, prop, level):
    update = True
    update_clause = ""
    while update is True:
        update = False
        for clause in clauses[level]:
            if len(clause) == 0:
                clauses[level] = [[]]
                return clauses, assignment, prop
            if len(clause) == 1:
                if clause[0] < 0:
                    prop[level].remove(-clause[0])
                    assignment[level][-clause[0]] = 0
                    update_clause = -clause[0]
                else:
                    prop[level].remove(clause[0])
                    assignment[level][clause[0]] = 1
                    update_clause = clause[0]
                update = True
                break
        if update:
            variable_assignment(clauses, assignment, update_clause, level)

"""
clauses is a list of list
assignment is dictionary
prop is a set
"""
def DPLL(clauses, assignment, prop, level):
    unit_prop(clauses, assignment, prop, level)
    if clauses[level] == [[]]:
        return "False", assignment[level].copy()
    elif clauses[level] == []:
        return "True", assignment[level].copy()
    else:
        literal = random.sample(prop[level], 1)[0]
        new_clauses = clauses[level].copy()
        new_clauses.append([literal].copy())
        if len(clauses) > level + 1:
            clauses[level + 1] = new_clauses.copy()
            assignment[level + 1] = assignment[level].copy()
            prop[level + 1] = prop[level].copy()
        else:
            clauses.append(new_clauses.copy())
            assignment.append(assignment[level].copy())
            prop.append(prop[level].copy())
        sat, new_assignment = DPLL(clauses, assignment, prop, level+1)
        if sat == "True":
            return "True", new_assignment
        else:
            new_clauses = clauses[level].copy()
            new_clauses.append([-literal].copy())
            clauses[level+1] = new_clauses.copy()
            assignment[level + 1] = assignment[level].copy()
            prop[level + 1] = prop[level].copy()
            return DPLL(clauses, assignment, prop, level+1)

