"""
CSV I/O module for grading system.

This module separates CSV parsing logic from file I/O operations,
making the parsing logic testable without requiring actual files.

Note: For file-based I/O, use read_questions_from_csv() and read_students_from_csv()
from grading.py. This module focuses on the parsing logic that can be tested with StringIO.
"""
import csv
from grading import Question, Student


def parse_questions_csv(csv_reader):
    """
    Parse questions from a CSV reader.

    Args:
        csv_reader: A csv.DictReader instance

    Returns:
        List[Question]: List of parsed questions

    Expected CSV columns: part, name, points, coefficient
    """
    questions = []
    for row in csv_reader:
        part = row['part']
        title = row['name']
        points = float(row['points'])
        coefficient = float(row['coefficient'])
        questions.append(Question(part, title, points, coefficient))
    return questions


def parse_students_csv(csv_reader):
    """
    Parse students from a CSV reader.

    Args:
        csv_reader: A csv.DictReader instance

    Returns:
        List[Student]: List of parsed students

    Expected CSV columns: last name, first name, email
    """
    students = []
    for row in csv_reader:
        last_name = row['last name']
        first_name = row['first name']
        email = row['email']
        students.append(Student(last_name, first_name, email))
    return students
