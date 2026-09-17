from jssp import jssp_solve

def main():
    jobs = [
        [(0, 3), (1, 2), (2, 2)],
        [(0, 2), (2, 1), (1, 4)],
        [(1, 4), (2, 3)]
    ]
    machines = [0, 1, 2]

    jssp_solve(jobs)

    pass

if __name__ == "__main__":
    main()
