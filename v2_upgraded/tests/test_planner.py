from datetime import date
from io import StringIO
from unittest.mock import patch

from v2_upgraded.stream_planner_v2 import parse_schedule


# A smart helper function to intercept 'open' calls dynamically
def mock_open_behavior(mock_read_content):
    def side_effect(file_path, mode="r", *args, **kwargs):
        if "r" in mode:
            return StringIO(mock_read_content)
        else:
            return StringIO()  # Provide a clean, open mock stream for write operations

    return side_effect


def test_parse_schedule_valid_data():
    """Test that correctly formatted input strings are successfully parsed."""
    mock_file_content = (
        "date: 2026-06-10 | game: Elden Ring | notes: Shadow of the Erdtree stream\n"
        "date: 2026-06-11 | game: Hollow Knight | notes: Steel Soul run\n"
    )

    # We patch Path.exists to pass through, and use side_effect for open()
    with (
        patch("builtins.open", side_effect=mock_open_behavior(mock_file_content)),
        patch("v2_upgraded.stream_planner_v2.Path.exists", return_value=True),
    ):
        result = parse_schedule("dummy_input.txt", "dummy_output.md")

    assert len(result) == 2
    assert result[0]["game"] == "Elden Ring"
    assert result[0]["date"] == date(2026, 6, 10)
    assert result[1]["notes"] == "Steel Soul run"


def test_parse_schedule_malformed_line():
    """Test that lines missing a pipe delimiter are skipped gracefully."""
    mock_file_content = (
        "date: 2026-06-10 | game: Elden Ring | notes: Clean line\n"
        "corrupt line here with no delimiters\n"
        "date: 2026-06-11 | game: Hollow Knight | notes: Another clean line\n"
    )

    with (
        patch("builtins.open", side_effect=mock_open_behavior(mock_file_content)),
        patch("v2_upgraded.stream_planner_v2.Path.exists", return_value=True),
    ):
        result = parse_schedule("dummy_input.txt", "dummy_output.md")

    assert len(result) == 2
    assert result[0]["game"] == "Elden Ring"
    assert result[1]["game"] == "Hollow Knight"


def test_parse_schedule_invalid_date_format(capsys):
    """Test that lines with unparseable dates log a warning and skip execution."""
    mock_file_content = "date: 06-12-2026 | game: Metroid | notes: Bad date format\n"

    with (
        patch("builtins.open", side_effect=mock_open_behavior(mock_file_content)),
        patch("v2_upgraded.stream_planner_v2.Path.exists", return_value=True),
    ):
        result = parse_schedule("dummy_input.txt", "dummy_output.md")

    assert len(result) == 0

    captured = capsys.readouterr()
    assert "[WARNING] Skipping line due to invalid date format" in captured.out
