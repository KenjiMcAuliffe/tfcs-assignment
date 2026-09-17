from jssp import JSSPSolver, Op

def main():

    jobs = (
        (Op(0, 0, 0, 3), Op(0, 1, 1, 2), Op(0, 2, 2, 2)),
        (Op(1, 0, 0, 2), Op(1, 1, 2, 1), Op(1, 2, 1, 4)),
        (Op(2, 0, 1, 4), Op(2, 1, 2, 3))
    )

    solver = JSSPSolver(jobs)
    res = solver.solve()

    if res is None:
        print("No possible schedule found")
    else:
        makespan, sched = res
        print(sched)
        print(f"makespan: {makespan}")

if __name__ == "__main__":
    main()
