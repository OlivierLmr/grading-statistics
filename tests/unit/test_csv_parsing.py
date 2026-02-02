"""
Unit tests for CSV parsing functions.

Tests the CSV parsing logic separated from file I/O using StringIO.
"""
import pytest
import csv
from io import StringIO
from grading_io import parse_questions_csv, parse_students_csv


@pytest.mark.unit
class TestParseQuestionsCSV:
    """Tests for parse_questions_csv function."""

    def test_parse_single_question(self):
        """Test parsing a CSV with a single question."""
        csv_data = "part,name,points,coefficient\nPart 1,Q1,10.0,1.0\n"
        reader = csv.DictReader(StringIO(csv_data))
        questions = parse_questions_csv(reader)

        assert len(questions) == 1
        assert questions[0].part == "Part 1"
        assert questions[0].title == "Q1"
        assert questions[0].points == 10.0
        assert questions[0].coefficient == 1.0

    def test_parse_multiple_questions(self):
        """Test parsing a CSV with multiple questions."""
        csv_data = """part,name,points,coefficient
Part 1,Question 1,10.0,1.0
Part 1,Question 2,15.0,1.0
Part 2,Question 3,20.0,1.5
"""
        reader = csv.DictReader(StringIO(csv_data))
        questions = parse_questions_csv(reader)

        assert len(questions) == 3
        assert questions[0].title == "Question 1"
        assert questions[1].title == "Question 2"
        assert questions[2].title == "Question 3"
        assert questions[2].coefficient == 1.5

    def test_parse_empty_csv(self):
        """Test parsing an empty CSV (headers only)."""
        csv_data = "part,name,points,coefficient\n"
        reader = csv.DictReader(StringIO(csv_data))
        questions = parse_questions_csv(reader)

        assert len(questions) == 0

    def test_parse_questions_with_decimal_points(self):
        """Test parsing questions with various decimal point values."""
        csv_data = """part,name,points,coefficient
Part 1,Q1,10.5,1.0
Part 2,Q2,7.25,0.5
Part 3,Q3,100.0,2.0
"""
        reader = csv.DictReader(StringIO(csv_data))
        questions = parse_questions_csv(reader)

        assert questions[0].points == 10.5
        assert questions[1].points == 7.25
        assert questions[1].coefficient == 0.5
        assert questions[2].points == 100.0
        assert questions[2].coefficient == 2.0

    def test_parse_questions_with_missing_column_raises_error(self):
        """Test that missing columns raise KeyError."""
        csv_data = "part,name,points\nPart 1,Q1,10.0\n"  # Missing coefficient
        reader = csv.DictReader(StringIO(csv_data))

        with pytest.raises(KeyError):
            parse_questions_csv(reader)

    def test_parse_questions_with_invalid_float_raises_error(self):
        """Test that invalid float values raise ValueError."""
        csv_data = "part,name,points,coefficient\nPart 1,Q1,invalid,1.0\n"
        reader = csv.DictReader(StringIO(csv_data))

        with pytest.raises(ValueError):
            parse_questions_csv(reader)


@pytest.mark.unit
class TestParseStudentsCSV:
    """Tests for parse_students_csv function."""

    def test_parse_single_student(self):
        """Test parsing a CSV with a single student."""
        csv_data = "last name,first name,email\nDoe,John,john.doe@example.com\n"
        reader = csv.DictReader(StringIO(csv_data))
        students = parse_students_csv(reader)

        assert len(students) == 1
        assert students[0].last_name == "Doe"
        assert students[0].first_name == "John"
        assert students[0].email == "john.doe@example.com"

    def test_parse_multiple_students(self):
        """Test parsing a CSV with multiple students."""
        csv_data = """last name,first name,email
Doe,John,john.doe@example.com
Smith,Jane,jane.smith@example.com
Johnson,Bob,bob.johnson@example.com
"""
        reader = csv.DictReader(StringIO(csv_data))
        students = parse_students_csv(reader)

        assert len(students) == 3
        assert students[0].email == "john.doe@example.com"
        assert students[1].email == "jane.smith@example.com"
        assert students[2].email == "bob.johnson@example.com"

    def test_parse_empty_csv(self):
        """Test parsing an empty CSV (headers only)."""
        csv_data = "last name,first name,email\n"
        reader = csv.DictReader(StringIO(csv_data))
        students = parse_students_csv(reader)

        assert len(students) == 0

    def test_parse_students_with_special_characters(self):
        """Test parsing students with special characters in names."""
        csv_data = """last name,first name,email
O'Brien,Seán,sean.obrien@example.com
Müller,François,francois.muller@example.com
"""
        reader = csv.DictReader(StringIO(csv_data))
        students = parse_students_csv(reader)

        assert len(students) == 2
        assert students[0].last_name == "O'Brien"
        assert students[0].first_name == "Seán"
        assert students[1].last_name == "Müller"
        assert students[1].first_name == "François"

    def test_parse_students_with_local_email(self):
        """Test parsing students with local-part email (no domain)."""
        csv_data = """last name,first name,email
Doe,John,john.doe
Smith,Jane,jane.smith
"""
        reader = csv.DictReader(StringIO(csv_data))
        students = parse_students_csv(reader)

        assert len(students) == 2
        assert students[0].email == "john.doe"
        assert students[1].email == "jane.smith"

    def test_parse_students_with_missing_column_raises_error(self):
        """Test that missing columns raise KeyError."""
        csv_data = "last name,first name\nDoe,John\n"  # Missing email
        reader = csv.DictReader(StringIO(csv_data))

        with pytest.raises(KeyError):
            parse_students_csv(reader)
