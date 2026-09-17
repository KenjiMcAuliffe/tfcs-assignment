from itertools import permutations
from dataclasses import dataclass

class JSSPSolver:

    def __init__(self, ops: OpSeq):
        self.ops = ops

    def solve(self) -> tuple[int, Sched] | None:
        sequences = permutations(self.ops)

        best_maketime: int | None = None
        best_schedule: Sched | None = None

        for sequence in sequences:
            scheduler = self.SeqScheduler(sequence)
            res = scheduler.generate_schedule()
            if res is not None:
                maketime, schedule = res
                if maketime is not None:
                    if best_maketime is None or maketime < best_maketime:
                        best_maketime = maketime
                        best_schedule = schedule
        if best_schedule is None or best_maketime is None:
            return None
        return (best_maketime, best_schedule)

    class SeqScheduler:
        def __init__(self, seq: OpSeq):
            self.seq: OpSeq = seq
            self.sched: Sched = {}
            self.maketime: int | None = None

        def generate_schedule(self) -> tuple[int, Sched] | None:
            for operation in self.seq:
                try:
                    self.insert_operation(operation)
                except Exception as e:
                    print(f"Discarding sequence. Reason: {e}")
                    return None
            self.maketime = self.calculate_maketime()
            return (self.maketime, self.sched)

        def insert_operation(self, op: Op):
            if(op.machine not in self.sched):
                self.sched[op.machine] = {}
            deps = tuple(op2 for op2 in self.seq if op2.job == op.job and op2.index < op.index)
            earliest_start = 0

            for dep in deps:
                if dep.machine not in self.sched or dep not in self.sched[dep.machine]:
                    raise Exception(f"Failed inserting operation '{op}'. Dependencies not found.")
                dep_end = self.sched[dep.machine][dep] + dep.duration
                if earliest_start is None or dep_end > earliest_start:
                    earliest_start = dep_end

            machine_ops = dict(sorted(self.sched[op.machine].items(), key=lambda item: item[1]))

            start_time = earliest_start
            for o, s in machine_ops.items():
                if start_time + op.duration <= s:
                    break
                start_time = max(start_time, s + o.duration)
            self.sched[op.machine][op] = start_time

        def calculate_maketime(self):
            return max(tuple(
                max(tuple(s + o.duration for o, s in machine_sched.items()))
                for machine_sched in self.sched.values()
            ))

@dataclass(frozen=True)
class Op:
    job: int
    index: int
    machine: int
    duration: int

    def __repr__(self) -> str:
        return f"(J{self.job}O{self.index})"

Sched = dict[int, dict[Op, int]]

OpSeq = tuple[Op, ...]

