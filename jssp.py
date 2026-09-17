from itertools import permutations
from dataclasses import dataclass

"""
Terminology:

Op = operation
Ops = operations

Sched = schedule; a mapping between operations and start times for each machine.

Seq = sequence; one possible ordering of all of the operations in a JSSP problem instance.

"""

class JSSPSolver:

    def __init__(self, jobs: tuple[tuple[Op, ...], ...]):

        self.jobs: tuple[tuple[Op, ...], ...] = jobs
        self.n_jobs = sum(len(job) for job in jobs)
        self.next_operation = [0 for _ in jobs]
        self.best_schedule: Sched | None = None
        self.best_makespan: Makespan | None = None

    def solve(self) -> tuple[Makespan, Sched] | None:
        
        self.solve_recurse([])

        # In the (impossible) case that no solution is found:
        if self.best_schedule is None or self.best_makespan is None:
            return None

        return (self.best_makespan, self.best_schedule)

    def solve_recurse(self, sequence):

        # We have reached full depth in the state-space tree by constructing a full sequence.
        # This is the recursive base case.
        if len(sequence) == self.n_jobs:

            # The scheduler takes a sequence and finds optimal starting times for operation when placed in order of sequence.
            scheduler = self.Scheduler(sequence, self)
            res = scheduler.generate_schedule()

            # If we beat the best solution so far, replace it
            if res is not None:
                makespan, schedule = res
                if self.best_makespan is None or makespan < self.best_makespan:
                    self.best_makespan = makespan
                    self.best_schedule = schedule
        else:
            for job_idx, job in enumerate(self.jobs):
                next_index = self.next_operation[job_idx]
                if(next_index != len(job)):
                    next_operation = job[next_index]
                    sequence.append(next_operation)
                    self.next_operation[job_idx] += 1
                    self.solve_recurse(sequence)
                    self.next_operation[job_idx] -= 1
                    sequence.pop()

    # Iterate through a provided sequence, placing each operation into the schedule at the earliest position possible.
    class Scheduler:

        def __init__(self, seq: list[Op], solver: JSSPSolver):
            self.seq: list[Op] = seq
            self.sched: Sched = {}
            self.solver: JSSPSolver = solver

        def generate_schedule(self) -> tuple[Makespan, Sched] | None:

            # Try to insert each operation into the schedule one-by-one, following the provided sequence.
            for operation in self.seq:
                try:
                    self.insert_operation(operation)
                except InvalidSequenceException:
                    return None

            return (self.calculate_makespan(), self.sched)

        def insert_operation(self, op: Op):
            
            # The schedule begins entirely empty - we must consider that a machine has not been encountered yet.
            if(op.machine not in self.sched):
                self.sched[op.machine] = {}

            # Machine ops: Start times (so far) for each operation which shares a machine with the operation we are trying to insert.
            machine_ops = self.sched[op.machine]

            # Machine ops sorted by start time (ascending).
            sorted_machine_ops = dict(sorted(machine_ops.items(), key=lambda item: item[1]))

            # See how far we need to move the operation forward until it doesn't overlap with any existing operations.
            start_time = self.get_earliest_start(op)
            for o, s in sorted_machine_ops.items():
                if start_time + op.duration <= s:
                    break
                start_time = max(start_time, s + o.duration)

            # Update the start time for the operation
            self.sched[op.machine][op] = start_time

        def get_earliest_start(self, op: Op) -> int:
            if op.index == 0:
                return 0
            prev = self.solver.jobs[op.job][op.index - 1]
            return self.sched[prev.machine][prev] + prev.duration

        # Calculate the end times of each operation and take the maximum
        def calculate_makespan(self) -> Makespan:

            return max(
                start + op.duration
                for machine_sched in self.sched.values()
                for op, start in machine_sched.items()
            )

@dataclass(frozen=True)
class Op:
    job: int
    index: int
    machine: int
    duration: int

    def __repr__(self):
        return f"{self.job}{self.index}"

Sched = dict[int, dict[Op, int]]

Seq = tuple[Op, ...]

Makespan = int

class InvalidSequenceException(Exception):
    pass
