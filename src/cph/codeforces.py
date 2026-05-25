import datetime
import sys
import tomllib
from typing import Annotated

import codeforces_api
import typer
from codeforces_api.types import Contest
from rich import print
from xdg_base_dirs import xdg_config_home

config_file = xdg_config_home() / "cph/config.toml"
try:
    with config_file.open("rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    print(f"Error: Config file not found at {config_file}.", file=sys.stderr)
    config = {}
except tomllib.TOMLDecodeError as e:
    print(f"Error: Failed to parse config file: {e}", file=sys.stderr)
    config = {}

cf_auth = config.get("auth", {}).get("codeforces")
if cf_auth is not None and "key" in cf_auth and "secret" in cf_auth:
    cf_api = codeforces_api.CodeforcesApi(cf_auth["key"], cf_auth["secret"])
else:
    print(
        "Warning: Codeforces API key/secret not found in config. "
        "Proceeding with unauthenticated requests, which may be limited."
    )
    cf_api = codeforces_api.CodeforcesApi()

app = typer.Typer()


def colorize(str: str, color: str):
    return f"[{color}]{str}[/{color}]"


def format_phase(phase: str):
    if phase == "BEFORE":
        color = "bold green"
    elif phase == "CODING":
        color = "bold yellow"
    elif phase == "FINISHED":
        color = "bold red"
    else:
        color = "yellow"
    return colorize(phase, color)


def format_contest(contest: Contest):
    header = f"[{contest.id}] {contest.name} - {format_phase(contest.phase)}\n"
    start_date = (
        f"Start: {datetime.datetime.fromtimestamp(contest.start_time_seconds)}"
        if contest.start_time_seconds
        else ""
    )
    duration = (
        f"Duration: {datetime.timedelta(seconds=contest.duration_seconds)}"
        if contest.duration_seconds
        else ""
    )
    timeinfo = f"{start_date} {duration}\n"

    until_start = (
        f"Until start: {datetime.timedelta(seconds=contest.relative_time_seconds * -1)}\n"
        if contest.relative_time_seconds and contest.relative_time_seconds < 0
        else ""
    )

    return header + timeinfo + until_start


@app.command(name="list")
def list_contest(
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="list length"),
    ] = 10,
):
    """
    List recent Codeforces contests
    """
    contests = cf_api.contest_list()
    if not contests:
        return
    for contest in contests[:limit]:
        if contest:
            print(format_contest(contest))
