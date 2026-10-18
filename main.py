from jssp import Operation, jssp_decision
from time import perf_counter

def main():

    jobs = [
        [Operation(0, 3), Operation(1, 2), Operation(2, 2)],
        [Operation(0, 2), Operation(2, 1), Operation(1, 4)],
        [Operation(1, 4), Operation(2, 3)]
    ]
    K = 10

    start = perf_counter()
    schedule_exists = jssp_decision(jobs, K)
    finish = perf_counter()
    elapsed = finish - start
    print(f"Elapsed: {elapsed} seconds")

    if schedule_exists:
        print(f"A schedule exists that has a makespan <= K={K}.")
    else:
        print(f"A schedule does not exist that has a makespan <= K={K}")

if __name__ == "__main__":
    main()
