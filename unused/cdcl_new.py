import copy

def pick_branching_variable(variables, level, total_branching_choices):
    if (variables[level][0], 1) in total_branching_choices[level]:
        return False, False
    elif (variables[level][0], 0) in total_branching_choices[level]:
        total_branching_choices[level].add((variables[level][0], 1))
        return variables[level][0], 1
    else:
        total_branching_choices[level].add((variables[level][0], 0))
        return variables[level][0], 0



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
    to_update = True
    while to_update:
        to_update = False
        for idx, clause in enumerate(clauses[level]):
            if len(clause) == 0:
                return clauses[0][idx]
            elif len(clause) == 1 and clause != "T":
                literal = list(clause)[0]
                update_value = 0 if literal < 0 else 1
                update_literal = abs(literal)
                variable_assignment(clauses, assignment, variables, level, update_literal, update_value, idx, total_history)
                to_update = True
                break
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


def conflict_analyze(conf_cls, total_history, assignment, clauses, level, update_literal, update_value):
    # initial_level = level
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
            assert abs(last_assigned) == update_literal
            pool_lits = []
        else:
            pool_clause = clauses[0][assignment[level][abs(last_assigned)][1]]
            pool_lits = [l for l in pool_clause if abs(l) not in done_lits]

    learnt = frozenset([l for l in curr_level_lits.union(prev_level_lits)])
    if prev_level_lits and update_value == 1:
        level = max([assignment[level][abs(x)][2] for x in prev_level_lits])
    else:
        level = level - 1
    return level, learnt


def CDCL(clauses, assignment, variables, branching_history, total_history, total_branching_choices):
    # Initialize variables
    level = 0

    # Run unit prop
    unsat_clause = unit_prop(clauses, assignment, variables, level, total_history)
    if unsat_clause is not None:
        return False

    # Backtrack seach loop
    while len(variables[level]) != 0:
        # Pick variable

        sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level+1)
        update_literal, update_value = pick_branching_variable(variables, level, total_branching_choices)
        sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level + 1)

        if update_literal is False:
            # No valid assignments on this level
            level -= 1
            if level < 0:
                return False
            backtrack(clauses, assignment, variables, level, branching_history, total_branching_choices, total_history)
            sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level + 1)

        else:
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
            unsat_clause = unit_prop(clauses, assignment, variables, level, total_history)

            sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level+1)
            if unsat_clause is not None:
                # level, learnt = conflict_analyze(unsat_clause, total_history, assignment, clauses, level, update_literal, update_value)
                level -= 1
                if level < 0:
                    return False
                backtrack(clauses, assignment, variables, level, branching_history, total_history, total_branching_choices)
                sanity_check(clauses, assignment, variables, branching_history, total_history, total_branching_choices, level + 1)

    return True
