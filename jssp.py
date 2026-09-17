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

    def __init__(self, ops: Seq):
        self.ops = ops

    def solve(self) -> tuple[Makespan, Sched] | None:

        # 'permutations' generates all possible re-orderings of the operations
        perms = permutations(self.ops)

        best_makespan: Makespan | None = None
        best_schedule: Sched | None = None

        for sequence in perms:

            # The scheduler takes a sequence and finds optimal starting times for operation when placed in order of sequence.
            scheduler = self.Scheduler(sequence)
            res = scheduler.generate_schedule()

            # If we beat the best solution so far, replace it
            if res is not None:
                makespan, schedule = res
                if best_makespan is None or makespan < best_makespan:
                    best_makespan = makespan
                    best_schedule = schedule

        # In the (impossible) case that no solution is found:
        if best_schedule is None or best_makespan is None:
            return None

        return (best_makespan, best_schedule)

    # Iterate through a provided sequence, placing each operation into the schedule at the earliest position possible.
    class Scheduler:

        def __init__(self, seq: Seq):
            self.seq: Seq = seq
            self.sched: Sched = {}
            self.prev_ops: dict[Op, Op | None] = {}
            self.ops_by_job_index = {
                (op.job, op.index): op
                for op in seq
            }

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

            # Get the previous operation
            prev = self.ops_by_job_index.get((op.job, op.index - 1))

            if prev is not None:
                # If the previous operation hasn't already been inserted to the schedule, abort.
                if prev.machine not in self.sched or prev not in self.sched[prev.machine]:
                    raise InvalidSequenceException(f"Failed inserting operation '{op}'. Previous operations not found.")
                earliest_start = self.sched[prev.machine][prev] + prev.duration
            else:
                earliest_start = 0

            # Machine ops: Start times (so far) for each operation which shares a machine with the operation we are trying to insert.
            machine_ops = self.sched[op.machine]

            # Machine ops sorted by start time (ascending).
            sorted_machine_ops = dict(sorted(machine_ops.items(), key=lambda item: item[1]))

            # See how far we need to move the operation forward until it doesn't overlap with any existing operations.
            for o, s in sorted_machine_ops.items():
                if earliest_start + op.duration <= s:
                    break
                earliest_start = max(earliest_start, s + o.duration)

            # Update the start time for the operation
            self.sched[op.machine][op] = earliest_start

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

    def __repr__(self) -> str:
        return f"(J{self.job}O{self.index})"

Sched = dict[int, dict[Op, int]]

Seq = tuple[Op, ...]

Makespan = int

class InvalidSequenceException(Exception):
    pass
