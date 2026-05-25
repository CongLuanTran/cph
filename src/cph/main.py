import subprocess
import sys
from itertools import zip_longest
from pathlib import Path
from shutil import which
from time import perf_counter
from typing import Annotated

import typer
from rich import print
from rich.table import Table
from xdg_base_dirs import xdg_config_home

from cph import contest

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})
app.add_typer(contest.app, name="contest")
folder = xdg_config_home() / "cph/templates"
inp = "INP"
out = "OUT"

language_name = {"py": "Python", "cpp": "C++"}


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None and len(ctx.args) == 0:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def new(
    language: Annotated[
        str,
        typer.Option("--language", "-l", help="language", prompt="Language"),
    ] = "py",
    problem: Annotated[
        str, typer.Option("--problem", "-p", help="problem name", prompt="Problem")
    ] = "A",
):
    """
    Create a new solution boilerplate
    """
    template = folder / f"template.{language}"
    if not template.exists():
        print("There is no template for this language")
        return

    file = Path(f"{problem}.{language}")

    if file.exists():
        typer.confirm(
            f"The file {file} already exists. Do you want to overide it?", abort=True
        )

    file.write_text(template.read_text())
    Path(f"{problem}.{inp}").touch()
    Path(f"{problem}.{out}").touch()

    print(f"Solution boilerplate create successfully for Problem {problem}")

    if language == "py" and not Path(".ruff.toml").exists():
        Path(".ruff.toml").write_text('[lint]\nignore = ["E731", "E741"]\n')


@app.command()
def run(
    solution: Annotated[Path | None, typer.Argument(help="solution file path")] = None,
    inp: Annotated[
        Path | None, typer.Option("--input", "-i", help="input file")
    ] = None,
    out: Annotated[
        Path | None, typer.Option("--output", "-o", help="output file")
    ] = None,
):
    """
    Run a solution file
    """
    # If the argument is empty, prompt for it
    if solution is None:
        solution = Path(typer.prompt("Solution file: "))

    language = solution.suffix.lstrip(".")
    problem = solution.stem
    if not solution.exists():
        typer.confirm(
            "The solution file doesn't exist. Do you want to create it instead?",
            abort=True,
        )
        new(language, problem)
        return

    # Handle compilation of the solution if needed
    if language == "cpp":
        start = perf_counter()
        subprocess.run(
            [
                "g++",
                "-std=c++11",
                "-O0",
                "-Wall",
                solution.name,
                "-o",
                solution.stem,
            ]
        )
        end = perf_counter()
        print(f"Compilation Time: {(end - start):.4f} seconds")

        exec = [Path(solution.stem).resolve().as_posix()]
    elif language == "py":
        if which("pypy3"):
            print("Using PyPy for execution")
            exec = ["pypy3", solution.name]
        else:
            print("PyPy not found, using CPython for execution")
            exec = ["python3", solution.name]
    else:
        print("Unsupported language")
        return

    # Handle input and output files
    if not inp:
        inp = Path(typer.prompt("Input file", solution.with_suffix(".INP")))
    if not inp.exists():
        print(f"Input file for problem {solution.stem} does not exist")
        return
    if not out:
        out = Path(typer.prompt("Output file", solution.with_suffix((".OUT"))))

    # Execute the solution
    print(
        f"Executing the solution for problem {solution.stem} in {language_name.get(language, language)}"
    )
    with (
        inp.open("r") as f_inp,
        out.open("w+") as f_out,
    ):
        try:
            start = perf_counter()
            subprocess.run(exec, stdin=f_inp, stdout=f_out)
            end = perf_counter()
            print(f"Execution Time: {(end - start):.4f} seconds")
        except subprocess.CalledProcessError as e:
            print(
                "Error: Unknown error occured while executing the solution",
                file=sys.stderr,
            )
            print(e, file=sys.stderr)
            return

    with (
        inp.open("r") as f_inp,
        out.open("r") as f_out,
    ):
        lines_inp = f_inp.readlines()
        lines_out = f_out.readlines()

    table = Table(show_header=True, header_style="bold green")
    table.add_column("Input", style="cyan", no_wrap=True)
    table.add_column("Output", style="magenta", no_wrap=True)

    for l1, l2 in zip_longest(lines_inp, lines_out, fillvalue=""):
        table.add_row(l1.rstrip(), l2.rstrip())

    print(table)


if __name__ == "__main__":
    app()
