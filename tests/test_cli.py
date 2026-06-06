import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from grade_tracker.cli import app
from grade_tracker import storage

runner = CliRunner()


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path, monkeypatch):
    """Redirect storage to a temp file so tests don't touch ~/.grade-tracker.json."""
    fake = tmp_path / "grade-tracker.json"
    monkeypatch.setattr(storage, "DATA_FILE", fake)
    return fake


# ---------------------------------------------------------------------------
# add-course
# ---------------------------------------------------------------------------


def test_add_course_success():
    result = runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    assert result.exit_code == 0
    assert "CS101" in result.output


def test_add_course_target_too_high():
    result = runner.invoke(app, ["add-course", "CS101", "--target", "101"])
    assert result.exit_code == 1
    assert "Target score must be between 0 and 100" in result.output


def test_add_course_target_negative():
    result = runner.invoke(app, ["add-course", "CS101", "--target", "-1"])
    assert result.exit_code == 1
    assert "Target score must be between 0 and 100" in result.output


def test_add_course_target_boundary_values():
    result = runner.invoke(app, ["add-course", "CS101", "--target", "0"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["add-course", "CS102", "--target", "100"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# add-assignment
# ---------------------------------------------------------------------------


def test_add_assignment_success_with_score():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    result = runner.invoke(
        app, ["add-assignment", "CS101", "Homework 1", "--weight", "20", "--score", "85"]
    )
    assert result.exit_code == 0
    assert "Homework 1" in result.output


def test_add_assignment_success_without_score():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    result = runner.invoke(
        app, ["add-assignment", "CS101", "Midterm", "--weight", "30"]
    )
    assert result.exit_code == 0


def test_add_assignment_missing_weight():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    result = runner.invoke(app, ["add-assignment", "CS101", "Homework 1"])
    assert result.exit_code == 1
    assert "Adding a weight is mandatory" in result.output


def test_add_assignment_invalid_weight():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    result = runner.invoke(
        app, ["add-assignment", "CS101", "Homework 1", "--weight", "150"]
    )
    assert result.exit_code == 1
    assert "Invalid weight or score" in result.output


def test_add_assignment_invalid_score():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    result = runner.invoke(
        app, ["add-assignment", "CS101", "Homework 1", "--weight", "20", "--score", "110"]
    )
    assert result.exit_code == 1
    assert "Invalid weight or score" in result.output


def test_add_assignment_course_not_found():
    result = runner.invoke(
        app, ["add-assignment", "UNKNOWN", "HW1", "--weight", "10"]
    )
    assert result.exit_code == 1
    assert "Course has not been added" in result.output


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------


def test_summary_no_courses():
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "No courses" in result.output


def test_summary_with_courses():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    runner.invoke(app, ["add-assignment", "CS101", "HW1", "--weight", "40", "--score", "80"])
    runner.invoke(app, ["add-assignment", "CS101", "HW2", "--weight", "60", "--score", "100"])
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "CS101" in result.output
    assert "90.0%" in result.output  # target
    # current = (80*40 + 100*60) / 100 = (3200 + 6000) / 100 = 92.0
    assert "92.0%" in result.output


def test_summary_ungraded_shows_na():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    runner.invoke(app, ["add-assignment", "CS101", "HW1", "--weight", "40"])
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "N/A" in result.output
    # Nothing graded yet, so remaining = 100 - 0 = 100%
    assert "100.0%" in result.output


def test_summary_remaining_weight():
    runner.invoke(app, ["add-course", "CS101", "--target", "80"])
    runner.invoke(app, ["add-assignment", "CS101", "HW1", "--weight", "30", "--score", "70"])
    runner.invoke(app, ["add-assignment", "CS101", "HW2", "--weight", "20"])  # ungraded
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    # Remaining = 100 - 30 (only graded weight) = 70
    assert "70.0%" in result.output


# ---------------------------------------------------------------------------
# needs
# ---------------------------------------------------------------------------


def test_needs_basic():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    runner.invoke(app, ["add-assignment", "CS101", "HW1", "--weight", "30", "--score", "80"])
    runner.invoke(app, ["add-assignment", "CS101", "Final", "--weight", "70"])
    result = runner.invoke(app, ["needs", "CS101"])
    assert result.exit_code == 0
    # needed = (90*100 - 80*30) / 70 = (9000 - 2400) / 70 = 94.3
    assert "94.3%" in result.output


def test_needs_weights_not_100():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    runner.invoke(app, ["add-assignment", "CS101", "HW1", "--weight", "30", "--score", "80"])
    result = runner.invoke(app, ["needs", "CS101"])
    assert result.exit_code == 1
    assert "Weights of all assignments should add up to 100" in result.output


def test_needs_course_not_found():
    result = runner.invoke(app, ["needs", "UNKNOWN"])
    assert result.exit_code == 1
    assert "Course has not been added" in result.output


def test_needs_all_graded():
    runner.invoke(app, ["add-course", "CS101", "--target", "90"])
    runner.invoke(app, ["add-assignment", "CS101", "HW1", "--weight", "60", "--score", "80"])
    runner.invoke(app, ["add-assignment", "CS101", "Final", "--weight", "40", "--score", "95"])
    result = runner.invoke(app, ["needs", "CS101"])
    assert result.exit_code == 0
    assert "All assignments have been graded" in result.output


def test_needs_multiple_ungraded():
    runner.invoke(app, ["add-course", "CS101", "--target", "85"])
    runner.invoke(app, ["add-assignment", "CS101", "HW1", "--weight", "20", "--score", "90"])
    runner.invoke(app, ["add-assignment", "CS101", "HW2", "--weight", "30"])  # ungraded
    runner.invoke(app, ["add-assignment", "CS101", "Final", "--weight", "50"])  # ungraded
    result = runner.invoke(app, ["needs", "CS101"])
    assert result.exit_code == 0
    # needed = (85*100 - 90*20) / 80 = (8500 - 1800) / 80 = 83.75
    assert "83.8%" in result.output
