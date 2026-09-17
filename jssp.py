from itertools import permutations, product
from dataclasses import dataclass

def jssp_solve(jobs):
    total_operations = sum([len(ops) for ops in jobs])
    next_op = [0 for _ in range(total_operations)]
    generate_schedules(jobs, [], next_op)

def generate_schedules(jobs, schedule, next_op):

    total_operations = sum([len(ops) for ops in jobs])
    if len(schedule) == total_operations:
        print(schedule)
        evaluate(schedule)
        return

    for job in range(len(jobs)):
        op = next_op[job]

        if op < len(jobs[job]):
            schedule.append((job, op))
            next_op[job] += 1

            generate_schedules(jobs, schedule, next_op)

            next_op[job] -= 1
            schedule.pop()

def evaluate(schedule):
    pass
