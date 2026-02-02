"""
Unit tests for GlobalSettings class.

Tests settings serialization, deserialization, and default behavior.
"""
import pytest
import json
from grading import GlobalSettings


@pytest.mark.unit
class TestGlobalSettings:
    """Tests for the GlobalSettings class."""

    def test_default_initialization(self):
        """Test creating GlobalSettings with default values."""
        settings = GlobalSettings()
        assert settings.bonus_points == 0.0
        assert settings.added_points == 0.0
        assert settings.dropped_questions == []
        assert settings.given_questions == []

    def test_initialization_with_values(self):
        """Test creating GlobalSettings with custom values."""
        settings = GlobalSettings(
            bonus_points=5.0,
            added_points=2.0,
            dropped_questions=[1, 3],
            given_questions=[2]
        )
        assert settings.bonus_points == 5.0
        assert settings.added_points == 2.0
        assert settings.dropped_questions == [1, 3]
        assert settings.given_questions == [2]

    def test_repr(self):
        """Test GlobalSettings string representation."""
        settings = GlobalSettings(bonus_points=5.0, dropped_questions=[1])
        repr_str = repr(settings)
        assert "GlobalSettings" in repr_str
        assert "bonus=5.0" in repr_str
        assert "dropped=[1]" in repr_str

    def test_to_json_creates_file(self, tmp_dir):
        """Test writing settings to JSON file."""
        settings = GlobalSettings(
            bonus_points=10.0,
            added_points=3.0,
            dropped_questions=[2, 4],
            given_questions=[1]
        )
        json_path = tmp_dir / "settings.json"

        settings.to_json(str(json_path))

        # Verify file was created
        assert json_path.exists()

        # Verify content
        with open(json_path, 'r') as f:
            data = json.load(f)
        assert data['bonus_points'] == 10.0
        assert data['added_points'] == 3.0
        assert data['dropped_questions'] == [2, 4]
        assert data['given_questions'] == [1]

    def test_from_json_reads_file(self, tmp_dir):
        """Test reading settings from JSON file."""
        json_path = tmp_dir / "settings.json"
        data = {
            'bonus_points': 7.5,
            'added_points': 1.5,
            'dropped_questions': [3],
            'given_questions': [1, 2]
        }
        with open(json_path, 'w') as f:
            json.dump(data, f)

        settings = GlobalSettings.from_json(str(json_path))

        assert settings.bonus_points == 7.5
        assert settings.added_points == 1.5
        assert settings.dropped_questions == [3]
        assert settings.given_questions == [1, 2]

    def test_from_json_nonexistent_file_returns_defaults(self):
        """Test that from_json returns default settings for nonexistent file."""
        settings = GlobalSettings.from_json("/nonexistent/path/settings.json")

        assert settings.bonus_points == 0.0
        assert settings.added_points == 0.0
        assert settings.dropped_questions == []
        assert settings.given_questions == []

    def test_from_json_partial_data_uses_defaults(self, tmp_dir):
        """Test that from_json uses defaults for missing fields."""
        json_path = tmp_dir / "settings.json"
        # Only include bonus_points, omit others
        data = {'bonus_points': 5.0}
        with open(json_path, 'w') as f:
            json.dump(data, f)

        settings = GlobalSettings.from_json(str(json_path))

        assert settings.bonus_points == 5.0
        assert settings.added_points == 0.0  # Default
        assert settings.dropped_questions == []  # Default
        assert settings.given_questions == []  # Default

    def test_json_roundtrip(self, tmp_dir):
        """Test writing and reading settings produces identical data."""
        json_path = tmp_dir / "settings.json"
        original = GlobalSettings(
            bonus_points=12.5,
            added_points=4.0,
            dropped_questions=[1, 2, 5],
            given_questions=[3, 4]
        )

        # Write and read back
        original.to_json(str(json_path))
        read_back = GlobalSettings.from_json(str(json_path))

        assert read_back.bonus_points == original.bonus_points
        assert read_back.added_points == original.added_points
        assert read_back.dropped_questions == original.dropped_questions
        assert read_back.given_questions == original.given_questions

    def test_from_json_malformed_json_raises_error(self, tmp_dir):
        """Test that malformed JSON raises an error."""
        json_path = tmp_dir / "bad_settings.json"
        with open(json_path, 'w') as f:
            f.write("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            GlobalSettings.from_json(str(json_path))

    def test_overwrite_existing_file(self, tmp_dir):
        """Test that to_json overwrites existing file."""
        json_path = tmp_dir / "settings.json"

        # Write first settings
        settings1 = GlobalSettings(bonus_points=5.0)
        settings1.to_json(str(json_path))

        # Write different settings
        settings2 = GlobalSettings(bonus_points=10.0)
        settings2.to_json(str(json_path))

        # Read back and verify overwrite happened
        read_back = GlobalSettings.from_json(str(json_path))
        assert read_back.bonus_points == 10.0

    def test_empty_lists_serialized_correctly(self, tmp_dir):
        """Test that empty lists are properly serialized and deserialized."""
        json_path = tmp_dir / "settings.json"
        settings = GlobalSettings(
            bonus_points=5.0,
            dropped_questions=[],
            given_questions=[]
        )

        settings.to_json(str(json_path))
        read_back = GlobalSettings.from_json(str(json_path))

        assert read_back.dropped_questions == []
        assert read_back.given_questions == []
