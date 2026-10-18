from typing import NamedTuple


class Operation(NamedTuple):
    machine: int
    duration: int


Job = list[Operation]
Precedence = tuple[int, int]
Schedule = dict[int, int]  # operation index -> start time


def jssp_decision(jobs: list[Job], K: int) -> bool:

    if K < 0:
        return False

    operations, precedences = flatten_job_list(jobs)

    if any(op.duration <= 0 for op in operations):
        raise ValueError("Operation durations must be positive.")

    predecessors = {
        after: before
        for before, after in precedences
    }

    return jssp_decision_recurse(
        operations=operations,
        predecessors=predecessors,
        K=K,
        schedule={},
        machine_available={},
    )


def jssp_decision_recurse(
    operations: list[Operation],
    predecessors: dict[int, int],
    K: int,
    schedule: Schedule,
    machine_available: dict[int, int],
) -> bool:

    if len(schedule) == len(operations):
        return True

    # Eligible operations have no predecessor, or their
    # predecessor has already been scheduled.
    eligible = [
        i
        for i in range(len(operations))
        if i not in schedule
        and (
            i not in predecessors
            or predecessors[i] in schedule
        )
    ]

    earliest_starts: dict[int, int] = {}

    for i in eligible:
        operation = operations[i]
        predecessor = predecessors.get(i)

        job_available = (
            0
            if predecessor is None
            else schedule[predecessor]
            + operations[predecessor].duration
        )

        earliest_starts[i] = max(
            job_available,
            machine_available.get(operation.machine, 0),
        )

    # Find the eligible operation with the earliest completion.
    pivot = min(
        eligible,
        key=lambda i: earliest_starts[i] + operations[i].duration,
    )

    pivot_machine = operations[pivot].machine
    pivot_finish = earliest_starts[pivot] + operations[pivot].duration

    # Operations on this machine that could start before
    # the pivot finishes compete for priority.
    conflict_set = [
        i
        for i in eligible
        if operations[i].machine == pivot_machine
        and earliest_starts[i] < pivot_finish
    ]

    for i in conflict_set:
        operation = operations[i]
        start = earliest_starts[i]
        finish = start + operation.duration

        if finish > K:
            continue

        # Copy the state so each branch is independent.
        next_schedule = schedule.copy()
        next_schedule[i] = start

        next_machine_available = machine_available.copy()
        next_machine_available[operation.machine] = finish

        if jssp_decision_recurse(
            operations,
            predecessors,
            K,
            next_schedule,
            next_machine_available,
        ):
            return True

    return False


def flatten_job_list(
    jobs: list[Job],
) -> tuple[list[Operation], list[Precedence]]:

    operations: list[Operation] = []
    precedences: list[Precedence] = []

    for job in jobs:
        previous = None

        for operation in job:
            current = len(operations)
            operations.append(operation)

            if previous is not None:
                precedences.append((previous, current))

            previous = current

    return operations, precedences


if __name__ == "__main__":
    jobs = [
        [Operation(0, 3), Operation(1, 2)],
        [Operation(1, 2), Operation(0, 1)],
    ]

    print(jssp_decision(jobs, K=4))  # False
    print(jssp_decision(jobs, K=5))  # True
