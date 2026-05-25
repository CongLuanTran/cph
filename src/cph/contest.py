import typer

from cph import codeforces

app = typer.Typer()
app.add_typer(codeforces.app, name="codeforces")
