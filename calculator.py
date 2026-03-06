from absence_calculator.core import solve, format_result, ALL_OPERATIONS


def interactive_calculator():
    print("=== Absence Calculator ===")
    print("Operations: +, -, *, /, erased")
    print("Notation: 5(0) = absent 5")
    print("Type 'ops' to see all operations")
    print("Type 'quit' to exit")
    print()

    while True:
        try:
            user_input = input("calc >> ").strip()
        except EOFError:
            break

        if not user_input:
            continue

        lower = user_input.lower()

        if lower == "quit" or lower == "exit":
            print("Goodbye!")
            break

        elif lower == "ops":
            for name, info in ALL_OPERATIONS.items():
                print(f"  {name.upper()} ({info['symbol']})")
                print(f"    Rule: {info['rule']}")
                for ex in info['examples']:
                    print(f"    {ex}")
                print()

        else:
            try:
                result = solve(user_input)
                print(f"  = {format_result(result)}")
            except Exception as e:
                print(f"  Error: {e}")

        print()


if __name__ == "__main__":
    interactive_calculator()
