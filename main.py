from collections import defaultdict


# https://stackoverflow.com/a/510364/7540548
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""

    def __init__(self) -> None:
        try:
            self.impl: _GetchWindows | _GetchUnix = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self) -> bytes:
        return self.impl()


class _GetchUnix:
    def __init__(self) -> None:
        import tty
        import sys

    def __call__(self) -> bytes:
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self) -> None:
        import msvcrt

    def __call__(self) -> bytes:
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


class InterpreterError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def interpret(input: str) -> None:
    memory_pointer = 0
    instruction_pointer = 0
    memory: defaultdict[int, int] = defaultdict(lambda: 0)
    loop_starts: dict[int, int] = dict()
    loop_ends: dict[int, int] = dict()

    def increment_pointer() -> None:
        nonlocal memory_pointer
        memory_pointer += 1

    def decrement_pointer() -> None:
        nonlocal memory_pointer
        memory_pointer -= 1

    def increment_value() -> None:
        memory[memory_pointer] += 1

    def decrement_value() -> None:
        memory[memory_pointer] -= 1

    def put_char() -> None:
        print(chr(memory[memory_pointer]), end="")

    def get_char() -> None:
        memory[memory_pointer] = ord(getch().decode("utf-8"))

    def loop_start() -> None:
        nonlocal instruction_pointer
        nonlocal loop_starts
        nonlocal loop_ends
        if memory[memory_pointer] == 0:
            if instruction_pointer in loop_starts:
                instruction_pointer = loop_starts[instruction_pointer]
            else:
                levels = 1
                loop_start = instruction_pointer
                instruction_pointer += 1
                while True:
                    if instruction_pointer >= len(input):
                        raise InterpreterError("matching ']' not found")
                    if input[instruction_pointer] == "[":
                        levels += 1
                    elif input[instruction_pointer] == "]":
                        levels -= 1
                    if levels == 0:
                        loop_starts[loop_start] = instruction_pointer
                        loop_ends[instruction_pointer] = loop_start
                        break
                    instruction_pointer += 1

    def loop_end() -> None:
        if memory[memory_pointer] != 0:
            nonlocal instruction_pointer
            nonlocal loop_ends
            if instruction_pointer in loop_ends:
                instruction_pointer = loop_ends[instruction_pointer]
            else:
                levels = 1
                loop_end = instruction_pointer
                instruction_pointer -= 1
                while True:
                    if instruction_pointer < 0:
                        raise InterpreterError("matching '[' not found")
                    if input[instruction_pointer] == "]":
                        levels += 1
                    elif input[instruction_pointer] == "[":
                        levels -= 1
                    if levels == 0:
                        loop_ends[loop_end] = instruction_pointer
                        loop_starts[instruction_pointer] = loop_end
                        break
                    instruction_pointer -= 1

    instructions = {
        ">": increment_pointer,
        "<": decrement_pointer,
        "+": increment_value,
        "-": decrement_value,
        ".": put_char,
        ",": get_char,
        "[": loop_start,
        "]": loop_end,
    }

    while True:
        char = input[instruction_pointer]
        if char in instructions:
            instructions[char]()
        instruction_pointer += 1
        if instruction_pointer >= len(input):
            break

    pass


PROGRAMS = {"Hello, world!": f"{'+' * ord('H')}.>"
            + f"{'+' * ord('e')}.>"
            + f"{'+' * ord('l')}.>"
            + f"{'+' * ord('l')}.>"
            + f"{'+' * ord('o')}.>"
            + f"{'+' * ord(',')}.>"
            + f"{'+' * ord(' ')}.>"
            + f"{'+' * ord('w')}.>"
            + f"{'+' * ord('o')}.>"
            + f"{'+' * ord('r')}.>"
            + f"{'+' * ord('l')}.>"
            + f"{'+' * ord('d')}.>"
            + f"{'+' * ord('!')}.>",
            "Simple Loop": f">{'+' * ord('L')}<+++++[>.<-]",
            }


def main() -> None:
    for name, program in PROGRAMS.items():
        print(f"Program '{name}': ", end="")
        interpret(program)
        print()


if __name__ == "__main__":
    main()
