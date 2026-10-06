import argparse

from arena.client import Service
from arena.match import play


def main():
    parser = argparse.ArgumentParser(description="Арена морского боя")
    parser.add_argument("--first", default="http://localhost:8000")
    parser.add_argument("--second", default="http://localhost:8001")
    parser.add_argument("--games", type=int, default=1)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    log = (lambda message: None) if args.quiet else print
    score = {"first": 0, "second": 0}

    for number in range(1, args.games + 1):
        print(f"--- партия {number}")
        result = play(Service("first", args.first), Service("second", args.second), log)
        if result["winner"] is not None:
            score[result["winner"]] += 1

    print(f"счёт: first {score['first']} — second {score['second']}")


if __name__ == "__main__":
    main()
