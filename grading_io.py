"""
CSV I/O module for grading system.

This module separates CSV parsing logic from file I/O operations,
making the parsing logic testable without requiring actual files.
"""
import csv
from typing import List
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


def read_questions_from_csv(file_path: str):
    """
    Read questions from a CSV file.

    This is a thin wrapper around parse_questions_csv that handles file I/O.

    Args:
        file_path: Path to the CSV file

    Returns:
        List[Question]: List of parsed questions
    """
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return parse_questions_csv(reader)


def read_students_from_csv(file_path: str):
    """
    Read students from a CSV file.

    This is a thin wrapper around parse_students_csv that handles file I/O.

    Args:
        file_path: Path to the CSV file

    Returns:
        List[Student]: List of parsed students
    """
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return parse_students_csv(reader)
