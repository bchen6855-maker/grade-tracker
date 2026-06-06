from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from grade_tracker import storage

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("add-course")
def add_course(
    name: str = typer.Argument(..., help="Course name"),
    target: float = typer.Option(..., "--target", "-t", help="Target grade (0-100)"),
):
    """Add a course with a target grade."""
    if not 0 <= target <= 100:
        typer.echo(
            "Target score must be between 0 and 100. "
            "Please re-add the course with a valid target score."
        )
        raise typer.Exit(1)

    data = storage.load()
    data["courses"][name] = {"target": target, "assignments": []}
    storage.save(data)
    typer.echo(f"Course '{name}' added with target {target}%.")


@app.command("add-assignment")
def add_assignment(
    course: str = typer.Argument(..., help="Course name"),
    assignment: str = typer.Argument(..., help="Assignment name"),
    weight: Optional[float] = typer.Option(None, "--weight", "-w", help="Weight (0-100)"),
    score: Optional[float] = typer.Option(None, "--score", "-s", help="Score (0-100)"),
):
    """Add an assignment to a course."""
    if weight is None:
        typer.echo("Adding a weight is mandatory.")
        raise typer.Exit(1)

    if not 0 <= weight <= 100 or (score is not None and not 0 <= score <= 100):
        typer.echo(
            "Invalid weight or score. "
            "Please enter a weight and a score as a number between 0 and 100."
        )
        raise typer.Exit(1)

    data = storage.load()
    if course not in data["courses"]:
        typer.echo(
            "Course has not been added. "
            "Please add the course before adding assignments for the course."
        )
        raise typer.Exit(1)

    data["courses"][course]["assignments"].append(
        {"name": assignment, "weight": weight, "score": score}
    )
    storage.save(data)
    typer.echo(f"Assignment '{assignment}' added to '{course}'.")


@app.command("summary")
def summary():
    """Print a summary table of all courses."""
    data = storage.load()

    if not data["courses"]:
        typer.echo("No courses added yet.")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Course")
    table.add_column("Current Grade")
    table.add_column("Target Grade")
    table.add_column("Remaining Weight")

    for name, course in data["courses"].items():
        graded = [a for a in course["assignments"] if a["score"] is not None]
        graded_weight = sum(a["weight"] for a in graded)

        if graded_weight > 0:
            current = sum(a["score"] * a["weight"] for a in graded) / graded_weight
            current_str = f"{current:.1f}%"
        else:
            current_str = "N/A"

        remaining = 100 - graded_weight
        table.add_row(
            name,
            current_str,
            f"{course['target']}%",
            f"{remaining:.1f}%",
        )

    console.print(table)


@app.command("needs")
def needs(
    course_name: str = typer.Argument(..., help="Course name"),
):
    """Calculate the score needed on remaining assignments to hit your target."""
    data = storage.load()

    if course_name not in data["courses"]:
        typer.echo(
            "Course has not been added. "
            "Please add the course before adding assignments for the course."
        )
        raise typer.Exit(1)

    course = data["courses"][course_name]
    assignments = course["assignments"]
    total_weight = sum(a["weight"] for a in assignments)

    if abs(total_weight - 100) > 1e-9:
        typer.echo(
            "Weights of all assignments should add up to 100. "
            "Please finish recording all of your assignments before using 'needs'"
        )
        raise typer.Exit(1)

    ungraded = [a for a in assignments if a["score"] is None]

    if not ungraded:
        graded_sum = sum(a["score"] * a["weight"] for a in assignments)
        current = graded_sum / 100
        typer.echo(
            f"All assignments have been graded. "
            f"Your current grade in '{course_name}' is {current:.1f}%."
        )
        return

    graded = [a for a in assignments if a["score"] is not None]
    graded_sum = sum(a["score"] * a["weight"] for a in graded)
    ungraded_weight = sum(a["weight"] for a in ungraded)
    target = course["target"]

    needed = (target * 100 - graded_sum) / ungraded_weight
    typer.echo(
        f"You need to score {needed:.1f}% on remaining assignments "
        f"to reach your target score in '{course_name}'."
    )
