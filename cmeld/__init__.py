import re
from pathlib import Path
from typing import List

import fire


def print_header(filepaths: List[str]):
    print("// Amalgamation of the following files:")
    for f in filepaths:
        print(f"//    {f}")


def print_section(name: str):
    name = f" {name} section "
    separator = bytearray("/* " + ("-" * 50) + " */", "utf-8")
    separator[6 : len(name)] = bytearray(name, "utf-8")
    print(bytes(separator).decode())
    print()


def remove_includes(lines: list[str]) -> list[str]:
    pattern = re.compile(r"^#include +\"[^\"]+\".*$")
    return [line for line in lines if pattern.match(line) is None]


def strip_first_empty_lines(lines: list[str]) -> list[str]:
    new_lines = []
    state = 0
    for line in lines:
        if state == 0 and len(line.strip()) == 0:
            continue
        if state == 0 and len(line.strip()) > 0:
            state += 1
        new_lines.append(line)
    return new_lines


def remove_trailing_empty_lines(lines: list[str]):
    lines = strip_first_empty_lines(list(reversed(lines)))
    lines = strip_first_empty_lines(list(reversed(lines)))
    return lines


class Meld:
    def headers(self, *files):
        filepaths = list(sorted(list(set([str(f) for f in files]))))
        print_header(filepaths)

        incl_patt = re.compile(r"^#include +\"[^\"]+\".*$")

        for file in filepaths:
            filepath = Path(file)
            with open(filepath, "r") as f:
                print_section(str(filepath.with_suffix("")))
                for line in f.readlines():
                    if incl_patt.match(line):
                        continue
                    print(line, end="")
                if file != filepaths[-1]:
                    print()

    def sources(self, header: str, *files):
        filepaths = list(sorted(list(set([str(f) for f in files]))))
        print_header(filepaths)

        print()
        print(f'#include "{header}.h" ')
        print()

        for file in filepaths:
            filepath = Path(file)
            with open(filepath, "r") as f:
                lines = remove_includes(f.readlines())
                lines = remove_trailing_empty_lines(lines)
                print_section(str(filepath.with_suffix("")))
                for line in lines:
                    print(line, end="")
                if file != filepaths[-1]:
                    print()


def main():
    fire.Fire(Meld)
