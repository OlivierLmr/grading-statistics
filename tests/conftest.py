"""
Shared pytest fixtures for grading statistics tests.

This module provides common fixtures used across all test modules.
"""
import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path to import grading module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from grading import Question, Student, Evaluation, Class, GlobalSettings, Results
from tests.fixtures.sample_data import (
    create_sample_questions,
    create_sample_students,
    create_sample_evaluation,
    create_sample_class,
    create_sample_settings,
    create_sample_results
)


@pytest.fixture
def sample_questions():
    """Fixture providing a list of sample questions."""
    return create_sample_questions()


@pytest.fixture
def sample_students():
    """Fixture providing a list of sample students."""
    return create_sample_students()


@pytest.fixture
def sample_evaluation():
    """Fixture providing a sample evaluation."""
    return create_sample_evaluation()


@pytest.fixture
def sample_class():
    """Fixture providing a sample class with students."""
    return create_sample_class()


@pytest.fixture
def sample_settings():
    """Fixture providing default GlobalSettings."""
    return create_sample_settings()


@pytest.fixture
def sample_settings_with_dropped():
    """Fixture providing GlobalSettings with dropped questions."""
    return create_sample_settings(dropped_questions=[2])


@pytest.fixture
def sample_settings_with_given():
    """Fixture providing GlobalSettings with given questions."""
    return create_sample_settings(given_questions=[1])


@pytest.fixture
def sample_settings_with_bonus():
    """Fixture providing GlobalSettings with bonus points."""
    return create_sample_settings(bonus_points=5.0)


@pytest.fixture
def sample_settings_complex():
    """Fixture providing GlobalSettings with multiple settings."""
    return create_sample_settings(
        bonus_points=5.0,
        added_points=2.0,
        dropped_questions=[3],
        given_questions=[1]
    )


@pytest.fixture
def sample_results(sample_class, sample_evaluation, sample_settings):
    """Fixture providing a sample Results instance."""
    return Results(sample_class, sample_evaluation, sample_settings)


@pytest.fixture
def tmp_dir():
    """Fixture providing a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_csv_files(tmp_dir):
    """Fixture providing paths for temporary CSV files."""
    return {
        'roster': tmp_dir / 'roster.csv',
        'questions': tmp_dir / 'questions.csv',
        'results': tmp_dir / 'results.csv',
        'settings': tmp_dir / 'settings.json'
    }
