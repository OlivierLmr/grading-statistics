"""
Unit tests for Question, Student, Evaluation, and Class models.

Tests the basic data models that form the foundation of the grading system.
"""
import pytest
from grading import Question, Student, Evaluation, Class


@pytest.mark.unit
class TestQuestion:
    """Tests for the Question class."""

    def test_question_creation(self):
        """Test creating a Question instance."""
        q = Question("Part 1", "Sample Question", 10.0, 1.0)
        assert q.part == "Part 1"
        assert q.title == "Sample Question"
        assert q.points == 10.0
        assert q.coefficient == 1.0

    def test_question_repr(self):
        """Test Question string representation."""
        q = Question("Part 1", "Test", 5.0, 2.0)
        expected = "Question(part='Part 1', title='Test', points=5.0, coefficient=2.0)"
        assert repr(q) == expected

    def test_question_with_different_coefficient(self):
        """Test Question with non-default coefficient."""
        q = Question("Part 2", "Weighted Question", 20.0, 1.5)
        assert q.coefficient == 1.5
        assert q.points == 20.0


@pytest.mark.unit
class TestStudent:
    """Tests for the Student class."""

    def test_student_creation(self):
        """Test creating a Student instance."""
        s = Student("Doe", "John", "john.doe@example.com")
        assert s.last_name == "Doe"
        assert s.first_name == "John"
        assert s.email == "john.doe@example.com"

    def test_student_repr(self):
        """Test Student string representation."""
        s = Student("Smith", "Jane", "jane@test.com")
        expected = "Student(last_name='Smith', first_name='Jane', email='jane@test.com')"
        assert repr(s) == expected

    def test_student_with_local_email(self):
        """Test Student with local-part email (no domain)."""
        s = Student("Johnson", "Bob", "bob.johnson")
        assert s.email == "bob.johnson"


@pytest.mark.unit
class TestEvaluation:
    """Tests for the Evaluation class."""

    def test_evaluation_creation(self, sample_questions):
        """Test creating an Evaluation instance."""
        eval = Evaluation("Midterm", sample_questions)
        assert eval.name == "Midterm"
        assert len(eval.questions) == 4
        assert eval.questions[0].title == "Question 1"

    def test_evaluation_repr(self, sample_questions):
        """Test Evaluation string representation."""
        eval = Evaluation("Test", sample_questions[:2])
        repr_str = repr(eval)
        assert "Evaluation(name='Test'" in repr_str
        assert "questions=" in repr_str

    def test_get_question_uid_valid(self, sample_evaluation):
        """Test getting question UID for valid question numbers."""
        assert sample_evaluation.get_question_uid(0) == "Q1"
        assert sample_evaluation.get_question_uid(1) == "Q2"
        assert sample_evaluation.get_question_uid(2) == "Q3"
        assert sample_evaluation.get_question_uid(3) == "Q4"

    def test_get_question_uid_invalid_negative(self, sample_evaluation):
        """Test getting question UID with negative index."""
        with pytest.raises(ValueError, match="Invalid question number"):
            sample_evaluation.get_question_uid(-1)

    def test_get_question_uid_invalid_out_of_range(self, sample_evaluation):
        """Test getting question UID with out-of-range index."""
        with pytest.raises(ValueError, match="Invalid question number"):
            sample_evaluation.get_question_uid(10)

    def test_get_question_uid_boundary(self, sample_evaluation):
        """Test getting question UID at boundaries."""
        # First question
        assert sample_evaluation.get_question_uid(0) == "Q1"
        # Last question (4 questions total, so index 3)
        assert sample_evaluation.get_question_uid(3) == "Q4"
        # Just beyond last question
        with pytest.raises(ValueError):
            sample_evaluation.get_question_uid(4)


@pytest.mark.unit
class TestClass:
    """Tests for the Class class."""

    def test_class_creation(self):
        """Test creating a Class instance."""
        cls = Class("CS101")
        assert cls.name == "CS101"
        assert cls.students == []

    def test_add_student(self):
        """Test adding a student to a class."""
        cls = Class("Test Class")
        student = Student("Doe", "John", "john@test.com")
        cls.add_student(student)
        assert len(cls.students) == 1
        assert cls.students[0] == student

    def test_add_multiple_students(self, sample_students):
        """Test adding multiple students to a class."""
        cls = Class("Test Class")
        for student in sample_students:
            cls.add_student(student)
        assert len(cls.students) == 3
        assert cls.students[0].email == "john.doe@example.com"
        assert cls.students[1].email == "jane.smith@example.com"
        assert cls.students[2].email == "bob.johnson@example.com"

    def test_class_repr(self):
        """Test Class string representation."""
        cls = Class("Test")
        student = Student("Doe", "John", "john@test.com")
        cls.add_student(student)
        repr_str = repr(cls)
        assert "Class(name='Test'" in repr_str
        assert "students=" in repr_str
