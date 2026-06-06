# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A command-line tool that helps students record assignment grades and calculate what grade they need on future assignments to reach a target overall grade.

## Tech stack

Python, managed by `uv`. CLI built with [Typer](https://typer.tiangolo.com/); table output via [Rich](https://rich.readthedocs.io/). Data persisted as JSON at `~/.grade-tracker.json`.

## Commands

```bash
uv sync --dev          # install deps (including pytest)
uv run grade-tracker   # run the CLI
uv run pytest          # run all tests
uv run pytest tests/test_cli.py::test_name -v  # single test
```

## Architecture

```
src/grade_tracker/
  cli.py      – Typer app with four subcommands: add-course, add-assignment, summary, needs
  storage.py  – load/save dict to ~/.grade-tracker.json
tests/
  test_cli.py – all tests via typer.testing.CliRunner; autouse fixture redirects DATA_FILE to tmp_path
```

Grade calculations live inline in `cli.py`:
- **current grade** (summary col 2): `sum(score * weight for graded) / sum(weight for graded)`
- **needed score** (needs): `(target * 100 - sum(score * weight for graded)) / sum(weight for ungraded)`

## Initial instructions

Please create a command-line tool for students to track their grades.
This project should be managed by uv, and installable uv add "git+https://github.com/bchen6855-maker/grade-tracker.git
Please use python to develop this project.

The command-line tool should work as follows:
    The root command should run the executable, which the user runs by typing `grade-tracker`.
    The user enters a name for the course. (needs a subcommand name `add-course` for this.)
        add-course should have a mandatory flag --target, or abbreviated -t, with the value being a number between 0 and 100, representing what grade the user wants to achieve in this class. If the value is something other than the above requirement, should throw an exception. It should exit with an error message: "Target score must be between 0 and 100. Please re-add the course with a valid target score."
    Then the user adds assignments/quizzes/exams, or whatever work that counts toward the total grade. (needs a subcommand named `add-assignment` for this).
        For the subcommand add-assignment, there should be the following positional arguments and flags:
            Positional arguments: 
                Position 1: the name of the course. Should refer to a course that has been added. Should match the exact course name. If that course has not been added, it should exit with an error message: "Course has not been added. Please add the course before adding assignments for the course."
                Position 2: the name of the assignment
            The subcommand add-assignment takes two flags, which should take numerical value between 0 and 100: --weight , or abbreviated as -w, to enter the weight of that assignment in the overall grade (--weight is a mandatory flag); and --score, or abbreviated as -s, to enter the score the user earned for that assignment (--score is optional. If not given a score, it means that the assignment hasn't yet been graded). If any one of the values for weight and score is something other than 0-100, it should exit with an error message: "Invalid weight or score. Please enter a weight and a score as a number between 0 and 100." If --weight is ommitted, it should exit with an error message: "Adding a weight is mandatory."
    


    There should be another subcommand named `summary`, which prints out a table in the termimal. Each row is a course that has been logged. The columns are as follows: column 1: course name | column 2: current overall grade (a number between 0 and 100, calculated by summing the products of each score and weight of graded assignments, then dividing by the total weight of graded assignments so far) | column 3: target overall grade the user wants to achieve in this class | column 4: remaining weights left (100 minus the sum of weights of the already graded assignments)

    Lastly, there should be a subcommand named `needs`, with an argument course-name. When the user types `grade-tracker course-name needs`, the tool should print out the following:
    You need to score (number between 0 and 100)% on remaining assignments to reach you target score in `course-name`. The score needed should be calculated as follows:
    (sum of the products of score and weight of graded assignments + score needed × weight of that assignment) / 100 = target score
    If there are more than one assignments ungraded, treat them as a single batch, and the batch weight as the sum of weights of individual assignments. Then calculate the score needed the same way as above. In this case, the score needed is essentially a score such that the weighted average of scores achieved in the remaining assignment should be this score needed.
    If the logged weights do not add up to 100, `needs` should throw an exception. It should exit with an error message: "Weights of all assignments should add up to 100. Please finish recording all of your assignments before using 'needs`"


As you build the tool, make git commits along the way after each step is done. 

Write and run tests to ensure that the tool works as intended.




