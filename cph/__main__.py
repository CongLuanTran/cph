from itertools import zip_longest
from resource import RUSAGE_CHILDREN, getrusage
from shutil import which
import subprocess
from pathlib import Path
from time import time

from rich.table import Table
import typer
from rich import print

app = typer.Typer()
folder = Path.home() / ".config/cph"
inp = "INP"
out = "OUT"

language_name = {"py": "Python", "cpp": "C++"}


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None and len(ctx.args) == 0:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def new(language: str = "py", problem: str = "A"):
    template = folder / f"template.{language}"
    if not template.exists():
        print("There is no template for this language")
        return

    Path(f"{problem}.{language}").write_text(template.read_text())
    Path(f"{problem}.{inp}").touch()
    Path(f"{problem}.{out}").touch()

    print(f"Solution boilerplate create successfully for Problem {problem}")

    if language == "py" and not Path(".ruff.toml").exists():
        Path(".ruff.toml").write_text('[lint]\nignore = ["E731", "E741"]\n')


@app.command()
def run(language: str = "py", problem: str = "A"):
    solution = Path(f"{problem}.{language}")
    if not solution.exists():
        typer.confirm(
            "There is no solution for this problem. Do you want to create it instead?",
            abort=True,
        )
        new(language, problem)
        return

    if language == "cpp":
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
        exec = [str(solution.with_suffix(""))]
    elif language == "py":
        if which("pypy3"):
            print("Using PyPy for execution")
            exec = ["pypy3", solution.name]
        else:
            print("PypY not found, using CPython for execution")
            exec = ["python3", solution.name]
    else:
        print("Unsupported language")
        return

    inp_path = Path(f"{problem}.{inp}")
    out_path = Path(f"{problem}.{out}")

    print(
        f"Executing the solution for problem {problem} in {language_name.get(language, language)}"
    )
    with (
        inp_path.open("r") as f_inp,
        out_path.open("w+") as f_out,
    ):
        try:
            subprocess.run(exec, stdin=f_inp, stdout=f_out)
            info = getrusage(RUSAGE_CHILDREN)
            print(f"CPU Time: {(info.ru_utime + info.ru_stime):.4f} seconds")
        except subprocess.CalledProcessError as e:
            print("Error occured while executing the solution")
            print(e)
            return

    with (
        inp_path.open("r") as f_inp,
        out_path.open("r") as f_out,
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
