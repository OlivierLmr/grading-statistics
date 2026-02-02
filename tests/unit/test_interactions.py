"""
Unit tests for user interaction abstraction.

Tests the MockInteraction class which is used for testing import logic.
"""
import pytest
from grading_interactions import MockInteraction, ConsoleInteraction


@pytest.mark.unit
class TestMockInteraction:
    """Tests for MockInteraction class."""

    def test_get_question_name_default(self):
        """Test getting question name with default value."""
        mock = MockInteraction()
        name = mock.get_question_name(1)
        assert name == "Question 1"

    def test_get_question_name_custom(self):
        """Test getting question name with custom value."""
        mock = MockInteraction({
            'question_names': {1: "Custom Question", 2: "Another Question"}
        })
        assert mock.get_question_name(1) == "Custom Question"
        assert mock.get_question_name(2) == "Another Question"
        assert mock.get_question_name(3) == "Question 3"  # Default

    def test_get_question_points_default(self):
        """Test getting question points with default value."""
        mock = MockInteraction()
        points = mock.get_question_points(1)
        assert points == 1.0

    def test_get_question_points_custom(self):
        """Test getting question points with custom value."""
        mock = MockInteraction({
            'question_points': {1: 10.0, 2: 15.5}
        })
        assert mock.get_question_points(1) == 10.0
        assert mock.get_question_points(2) == 15.5
        assert mock.get_question_points(3) == 1.0  # Default

    def test_handle_unknown_students_default(self):
        """Test handling unknown students with default choice (ignore)."""
        mock = MockInteraction()
        choice = mock.handle_unknown_students(["email1@test.com", "email2@test.com"])
        assert choice == '1'  # Default: ignore

    def test_handle_unknown_students_custom_choices(self):
        """Test handling unknown students with custom choices."""
        # Choice 2: Add to roster
        mock_add = MockInteraction({'unknown_students_choice': '2'})
        assert mock_add.handle_unknown_students(["email@test.com"]) == '2'

        # Choice 3: Override roster
        mock_override = MockInteraction({'unknown_students_choice': '3'})
        assert mock_override.handle_unknown_students(["email@test.com"]) == '3'

    def test_get_student_name_default(self):
        """Test getting student name with default (empty) value."""
        mock = MockInteraction()
        first, last = mock.get_student_name("email@test.com")
        assert first == ""
        assert last == ""

    def test_get_student_name_custom(self):
        """Test getting student name with custom values."""
        mock = MockInteraction({
            'student_names': {
                "john.doe": ("John", "Doe"),
                "jane.smith": ("Jane", "Smith")
            }
        })
        first, last = mock.get_student_name("john.doe")
        assert first == "John"
        assert last == "Doe"

        first, last = mock.get_student_name("jane.smith")
        assert first == "Jane"
        assert last == "Smith"

    def test_confirm_action_default(self):
        """Test confirm action with default (False) value."""
        mock = MockInteraction()
        confirmed = mock.confirm_action("Do something?")
        assert confirmed is False

    def test_confirm_action_custom(self):
        """Test confirm action with custom values."""
        mock = MockInteraction({
            'confirmations': {
                "Proceed?": True,
                "Delete?": False
            }
        })
        assert mock.confirm_action("Proceed?") is True
        assert mock.confirm_action("Delete?") is False
        assert mock.confirm_action("Unknown?") is False  # Default

    def test_interaction_tracking(self):
        """Test that interactions are tracked for verification."""
        mock = MockInteraction({
            'question_names': {1: "Q1"},
            'question_points': {1: 10.0},
            'student_names': {"email": ("First", "Last")},
            'unknown_students_choice': '2',
            'confirmations': {"Proceed?": True}
        })

        # Perform various interactions
        mock.get_question_name(1)
        mock.get_question_points(1)
        mock.handle_unknown_students(["email@test.com"])
        mock.get_student_name("email")
        mock.confirm_action("Proceed?")

        # Verify all interactions were tracked
        assert len(mock.interactions) == 5
        assert mock.interactions[0] == ('get_question_name', 1)
        assert mock.interactions[1] == ('get_question_points', 1)
        assert mock.interactions[2] == ('handle_unknown_students', ["email@test.com"])
        assert mock.interactions[3] == ('get_student_name', "email")
        assert mock.interactions[4] == ('confirm_action', "Proceed?")

    def test_multiple_question_interactions(self):
        """Test handling multiple question name/points requests."""
        mock = MockInteraction({
            'question_names': {1: "Q1", 2: "Q2", 3: "Q3"},
            'question_points': {1: 10.0, 2: 15.0, 3: 20.0}
        })

        for i in range(1, 4):
            name = mock.get_question_name(i)
            points = mock.get_question_points(i)
            assert name == f"Q{i}"
            assert points == float(i * 5 + 5)

    def test_empty_responses_dict(self):
        """Test MockInteraction with empty responses dictionary."""
        mock = MockInteraction({})

        assert mock.get_question_name(1) == "Question 1"
        assert mock.get_question_points(1) == 1.0
        assert mock.handle_unknown_students([]) == '1'
        assert mock.get_student_name("email") == ("", "")
        assert mock.confirm_action("Question?") is False


@pytest.mark.unit
class TestConsoleInteraction:
    """Basic tests for ConsoleInteraction (minimal, as it requires actual input)."""

    def test_console_interaction_exists(self):
        """Test that ConsoleInteraction can be instantiated."""
        console = ConsoleInteraction()
        assert console is not None
        assert isinstance(console, ConsoleInteraction)

    def test_console_interaction_has_required_methods(self):
        """Test that ConsoleInteraction implements all required methods."""
        console = ConsoleInteraction()
        assert hasattr(console, 'get_question_name')
        assert hasattr(console, 'get_question_points')
        assert hasattr(console, 'handle_unknown_students')
        assert hasattr(console, 'get_student_name')
        assert hasattr(console, 'confirm_action')
        assert callable(console.get_question_name)
        assert callable(console.get_question_points)
        assert callable(console.handle_unknown_students)
        assert callable(console.get_student_name)
        assert callable(console.confirm_action)
