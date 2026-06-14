import pytest
from pydantic import ValidationError

from watch_stream import StreamTelemetry


# --- Test Case 1: Valid Data Payloads ---
def test_valid_telemetry_payload():
    """Asserts that perfectly structured payloads pass scheme validation smoothly."""
    valid_data = {"viewer_count": 150, "bitrate_kbps": 4500}
    # If this initializes without throwing an error, the test passes
    payload = StreamTelemetry(**valid_data)

    assert payload.viewer_count == 150
    assert payload.bitrate_kbps == 4500


# --- Test Case 2: Negative Viewer Counts (Boundary Test) ---
def test_invalid_negative_viewer_count():
    """Asserts that negative viewer counts are aggressively blocked by the gatekeeper."""
    invalid_data = {"viewer_count": -5, "bitrate_kbps": 5000}
    # We EXPECT a ValidationError to be thrown here
    with pytest.raises(ValidationError) as exc_info:
        StreamTelemetry(**invalid_data)

    # Verify that the error message targets exact issue
    assert "Viewer count must be a positive integer" in str(exc_info.value)


# --- Test Case 3: Bitrate Floor Ceiling Constraints ---
@pytest.mark.parametrize(
    "bad_bitrate, expected_error",
    [
        (150, "Bitrate must be between 1,000 and 12,000 Kbps"),
        (15000, "Bitrate must be between 1,000 and 12,000 Kbps"),
    ],
)
def test_bitrate_boundary_constraints(bad_bitrate, expected_error):
    """Asserts that bitrates outside the corporate standard boundaries are rejected."""
    invalid_data = {"viewer_count": 50, "bitrate_kbps": bad_bitrate}
    with pytest.raises(ValidationError) as exc_info:
        StreamTelemetry(**invalid_data)

    assert expected_error in str(exc_info.value)
