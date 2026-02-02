"""
Integration tests for CSV I/O round-trip operations.

Tests that data can be written to CSV and read back without loss.
"""
import pytest
from grading import Evaluation, Class, Student, read_questions_from_csv, read_students_from_csv


@pytest.mark.integration
class TestEvaluationCSVRoundTrip:
    """Tests for Evaluation CSV write/read round-trip."""

    def test_evaluation_write_and_read(self, sample_evaluation, tmp_dir):
        """Test writing an evaluation to CSV and reading it back."""
        csv_path = tmp_dir / "questions.csv"

        # Write evaluation to CSV
        sample_evaluation.write_to_csv(str(csv_path))

        # Read it back
        questions = read_questions_from_csv(str(csv_path))

        # Verify questions match
        assert len(questions) == len(sample_evaluation.questions)
        for original, read_back in zip(sample_evaluation.questions, questions):
            assert original.part == read_back.part
            assert original.title == read_back.title
            assert original.points == read_back.points
            assert original.coefficient == read_back.coefficient

    def test_evaluation_from_csv_class_method(self, sample_evaluation, tmp_dir):
        """Test Evaluation.from_csv class method."""
        csv_path = tmp_dir / "questions.csv"

        # Write original evaluation
        sample_evaluation.write_to_csv(str(csv_path))

        # Read using from_csv class method
        read_eval = Evaluation.from_csv("Test", str(csv_path))

        assert read_eval.name == "Test"
        assert len(read_eval.questions) == len(sample_evaluation.questions)
        for original, read_back in zip(sample_evaluation.questions, read_eval.questions):
            assert original.part == read_back.part
            assert original.title == read_back.title
            assert original.points == read_back.points
            assert original.coefficient == read_back.coefficient

    def test_create_sample_evaluation(self, tmp_dir):
        """Test creating a sample evaluation file."""
        csv_path = tmp_dir / "sample_questions.csv"

        # Create sample evaluation
        Evaluation.create_sample_evaluation(str(csv_path))

        # Verify file was created
        assert csv_path.exists()

        # Read and verify content
        questions = read_questions_from_csv(str(csv_path))
        assert len(questions) == 1
        assert questions[0].part == "Part 1"
        assert questions[0].title == "Sample Question"
        assert questions[0].points == 10.0
        assert questions[0].coefficient == 1.0


@pytest.mark.integration
class TestClassCSVRoundTrip:
    """Tests for Class CSV write/read round-trip."""

    def test_class_write_and_read(self, sample_class, tmp_dir):
        """Test writing a class to CSV and reading it back."""
        csv_path = tmp_dir / "roster.csv"

        # Write class to CSV
        sample_class.write_to_csv(str(csv_path))

        # Read it back
        students = read_students_from_csv(str(csv_path))

        # Verify students match
        assert len(students) == len(sample_class.students)
        for original, read_back in zip(sample_class.students, students):
            assert original.last_name == read_back.last_name
            assert original.first_name == read_back.first_name
            assert original.email == read_back.email

    def test_class_from_csv_class_method(self, sample_class, tmp_dir):
        """Test Class.from_csv class method."""
        csv_path = tmp_dir / "roster.csv"

        # Write original class
        sample_class.write_to_csv(str(csv_path))

        # Read using from_csv class method
        read_class = Class.from_csv("Test Class", str(csv_path))

        assert read_class.name == "Test Class"
        assert len(read_class.students) == len(sample_class.students)
        for original, read_back in zip(sample_class.students, read_class.students):
            assert original.last_name == read_back.last_name
            assert original.first_name == read_back.first_name
            assert original.email == read_back.email

    def test_create_sample_class(self, tmp_dir):
        """Test creating a sample class file."""
        csv_path = tmp_dir / "sample_roster.csv"

        # Create sample class
        Class.create_sample_class(str(csv_path))

        # Verify file was created
        assert csv_path.exists()

        # Read and verify content
        students = read_students_from_csv(str(csv_path))
        assert len(students) == 1
        assert students[0].last_name == "Lemer"
        assert students[0].first_name == "Olivier"
        assert students[0].email == "olivier.lemer@example.com"

    def test_csv_roundtrip_preserves_order(self, tmp_dir):
        """Test that CSV round-trip preserves student order."""
        csv_path = tmp_dir / "roster.csv"

        # Create a class with specific order
        cls = Class("Test")
        cls.add_student(Student("Zebra", "Zoe", "zoe@test.com"))
        cls.add_student(Student("Apple", "Adam", "adam@test.com"))
        cls.add_student(Student("Middle", "Mike", "mike@test.com"))

        # Write and read back
        cls.write_to_csv(str(csv_path))
        read_class = Class.from_csv("Test", str(csv_path))

        # Verify order is preserved
        assert read_class.students[0].last_name == "Zebra"
        assert read_class.students[1].last_name == "Apple"
        assert read_class.students[2].last_name == "Middle"


@pytest.mark.integration
class TestCSVFileHandling:
    """Tests for CSV file handling edge cases."""

    def test_read_from_nonexistent_file_raises_error(self):
        """Test that reading from nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_questions_from_csv("/nonexistent/path/questions.csv")

        with pytest.raises(FileNotFoundError):
            read_students_from_csv("/nonexistent/path/roster.csv")

    def test_overwrite_existing_file(self, sample_evaluation, tmp_dir):
        """Test that writing to an existing file overwrites it."""
        csv_path = tmp_dir / "questions.csv"

        # Write first evaluation
        sample_evaluation.write_to_csv(str(csv_path))
        questions1 = read_questions_from_csv(str(csv_path))

        # Modify and write again
        sample_evaluation.questions[0].title = "Modified Question"
        sample_evaluation.write_to_csv(str(csv_path))
        questions2 = read_questions_from_csv(str(csv_path))

        # Verify overwrite happened
        assert questions1[0].title != questions2[0].title
        assert questions2[0].title == "Modified Question"
