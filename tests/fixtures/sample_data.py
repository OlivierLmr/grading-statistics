"""
Sample data generators for testing.

This module provides functions to generate sample questions, students, evaluations,
classes, and results for testing purposes.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grading import Question, Student, Evaluation, Class, GlobalSettings, Results


def create_sample_questions():
    """Create a list of sample questions for testing."""
    return [
        Question("Part 1", "Question 1", 10.0, 1.0),
        Question("Part 1", "Question 2", 15.0, 1.0),
        Question("Part 2", "Question 3", 20.0, 1.0),
        Question("Part 2", "Question 4", 5.0, 1.0),
    ]


def create_sample_students():
    """Create a list of sample students for testing."""
    return [
        Student("Doe", "John", "john.doe@example.com"),
        Student("Smith", "Jane", "jane.smith@example.com"),
        Student("Johnson", "Bob", "bob.johnson@example.com"),
    ]


def create_sample_evaluation(name="Test Evaluation"):
    """Create a sample evaluation with predefined questions."""
    evaluation = Evaluation(name, create_sample_questions())
    return evaluation


def create_sample_class(name="Test Class"):
    """Create a sample class with predefined students."""
    class_ = Class(name)
    for student in create_sample_students():
        class_.add_student(student)
    return class_


def create_sample_settings(**kwargs):
    """Create a GlobalSettings instance with optional overrides."""
    defaults = {
        'bonus_points': 0.0,
        'added_points': 0.0,
        'dropped_questions': [],
        'given_questions': []
    }
    defaults.update(kwargs)
    return GlobalSettings(**defaults)


def create_sample_results(class_=None, evaluation=None, settings=None):
    """Create a sample Results instance."""
    if class_ is None:
        class_ = create_sample_class()
    if evaluation is None:
        evaluation = create_sample_evaluation()
    if settings is None:
        settings = create_sample_settings()
    return Results(class_, evaluation, settings)
