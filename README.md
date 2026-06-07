# grade-tracker

A command-line tool that helps students record assignment grades and calculate what score they need on remaining assignments to reach their target grade.

## Installation

```bash
uv tool install "git+https://github.com/bchen6855-maker/grade-tracker.git"
```

## Usage

### Add a course

```bash
grade-tracker add-course "DSC10" --target 90
```

`--target` / `-t` is required and must be between 0 and 100.

### Add an assignment

```bash
grade-tracker add-assignment "DSC10" "Midterm" --weight 30 --score 84
grade-tracker add-assignment "DSC10" "Final Exam" --weight 50
```

`--weight` / `-w` is required (0–100). `--score` / `-s` is optional — omit it for assignments not yet graded.

### View summary

```bash
grade-tracker summary
```

Prints a table with each course's current grade, target grade, and remaining ungraded weight.

### Calculate needed score

```bash
grade-tracker needs "DSC10"
```

Prints the score you need to average on all ungraded assignments to hit your target. Requires that all assignment weights sum to 100.

## Example session

```
$ grade-tracker add-course "DSC10" --target 90
Course 'DSC10' added with target 90.0%.

$ grade-tracker add-assignment "DSC10" "Homework 1" --weight 10 --score 88
$ grade-tracker add-assignment "DSC10" "Midterm"    --weight 40 --score 84
$ grade-tracker add-assignment "DSC10" "Final Exam" --weight 50

$ grade-tracker summary
┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Course┃ Current Grade ┃ Target Grade ┃ Remaining Weight ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ DSC10 │ 84.4%         │ 90.0%        │ 50.0%            │
└───────┴───────────────┴──────────────┴──────────────────┘

$ grade-tracker needs "DSC10"
You need to score 94.9% on remaining assignments to reach your target score in 'DSC10'.
```

## Data storage

Grades are saved to `~/.grade-tracker.json`.
