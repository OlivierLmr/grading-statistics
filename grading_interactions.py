"""
User interaction abstraction for grading system.

This module provides an abstraction layer for user interactions, allowing
the import and workflow functions to be tested without actual user input.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any


class UserInteraction(ABC):
    """Abstract interface for user interaction."""

    @abstractmethod
    def get_question_name(self, question_num: int) -> str:
        """
        Prompt user for question name.

        Args:
            question_num: 1-based question number

        Returns:
            Question name as string
        """
        pass

    @abstractmethod
    def get_question_points(self, question_num: int) -> float:
        """
        Prompt user for question points.

        Args:
            question_num: 1-based question number

        Returns:
            Points for the question (default 1.0)
        """
        pass

    @abstractmethod
    def handle_unknown_students(self, unknown_emails: List[str]) -> str:
        """
        Prompt user how to handle unknown students.

        Args:
            unknown_emails: List of unknown student email addresses

        Returns:
            Choice as string: '1' (ignore), '2' (add), or '3' (override)
        """
        pass

    @abstractmethod
    def get_student_name(self, email: str) -> Tuple[str, str]:
        """
        Prompt user for student name when email doesn't follow pattern.

        Args:
            email: Student email or local part

        Returns:
            Tuple of (first_name, last_name)
        """
        pass

    @abstractmethod
    def confirm_action(self, prompt: str) -> bool:
        """
        Ask user for yes/no confirmation.

        Args:
            prompt: Question to ask user

        Returns:
            True if user confirms, False otherwise
        """
        pass


class ConsoleInteraction(UserInteraction):
    """Production implementation using console input()."""

    def get_question_name(self, question_num: int) -> str:
        """Prompt user for question name via console."""
        try:
            question_name = input(f"  Question {question_num} name: ").strip()
            if not question_name:
                question_name = f"Question {question_num}"
        except EOFError:
            question_name = f"Question {question_num}"
        return question_name

    def get_question_points(self, question_num: int) -> float:
        """Prompt user for question points via console."""
        try:
            points_input = input(f"  Question {question_num} points (default 1.0): ").strip()
            if points_input:
                return float(points_input)
        except (EOFError, ValueError):
            # On input error or invalid numeric value, fall back to the default
            pass
        return 1.0

    def handle_unknown_students(self, unknown_emails: List[str]) -> str:
        """Prompt user how to handle unknown students via console."""
        print(f"\nFound {len(unknown_emails)} unknown student(s) not in roster:")
        for email in unknown_emails:
            print(f"  - {email}")

        print("\nWhat would you like to do with these unknown students?")
        print("  1. Ignore them (skip importing their scores)")
        print("  2. Add them to the roster (and import their scores)")
        print("  3. Override the roster with only these students")

        try:
            choice = input("Enter your choice (1/2/3): ").strip()
        except EOFError:
            choice = '1'

        return choice

    def get_student_name(self, email: str) -> Tuple[str, str]:
        """Prompt user for student name via console."""
        print(f"\nWarning: '{email}' doesn't follow 'first.last@email.com' pattern")
        try:
            name_input = input(f"  Please enter name in 'first last' format for {email}: ").strip()
            name_parts = name_input.split(maxsplit=1)
            if len(name_parts) >= 2:
                first_name = name_parts[0].capitalize()
                last_name = name_parts[1].capitalize()
            elif len(name_parts) == 1:
                first_name = name_parts[0].capitalize()
                last_name = ""
            else:
                first_name = ""
                last_name = ""
        except EOFError:
            first_name = ""
            last_name = ""

        return first_name, last_name

    def confirm_action(self, prompt: str) -> bool:
        """Ask user for yes/no confirmation via console."""
        try:
            resp = input(prompt + ' [y/N]: ').strip().lower()
        except EOFError:
            return False
        return resp in ('y', 'yes')


class MockInteraction(UserInteraction):
    """Test implementation with pre-programmed responses."""

    def __init__(self, responses: Dict[str, Any] = None):
        """
        Initialize with pre-programmed responses.

        Args:
            responses: Dictionary mapping interaction types to responses
                - 'question_names': Dict[int, str] - question number -> name
                - 'question_points': Dict[int, float] - question number -> points
                - 'unknown_students_choice': str - '1', '2', or '3'
                - 'student_names': Dict[str, Tuple[str, str]] - email -> (first, last)
                - 'confirmations': Dict[str, bool] - prompt -> True/False
        """
        self.responses = responses or {}
        self.question_names = self.responses.get('question_names', {})
        self.question_points = self.responses.get('question_points', {})
        self.unknown_students_choice = self.responses.get('unknown_students_choice', '1')
        self.student_names = self.responses.get('student_names', {})
        self.confirmations = self.responses.get('confirmations', {})

        # Track interactions for verification in tests
        self.interactions = []

    def get_question_name(self, question_num: int) -> str:
        """Return pre-programmed question name."""
        self.interactions.append(('get_question_name', question_num))
        return self.question_names.get(question_num, f"Question {question_num}")

    def get_question_points(self, question_num: int) -> float:
        """Return pre-programmed question points."""
        self.interactions.append(('get_question_points', question_num))
        return self.question_points.get(question_num, 1.0)

    def handle_unknown_students(self, unknown_emails: List[str]) -> str:
        """Return pre-programmed choice for unknown students."""
        self.interactions.append(('handle_unknown_students', unknown_emails))
        return self.unknown_students_choice

    def get_student_name(self, email: str) -> Tuple[str, str]:
        """Return pre-programmed student name."""
        self.interactions.append(('get_student_name', email))
        return self.student_names.get(email, ("", ""))

    def confirm_action(self, prompt: str) -> bool:
        """Return pre-programmed confirmation."""
        self.interactions.append(('confirm_action', prompt))
        # Default to False unless explicitly set to True
        return self.confirmations.get(prompt, False)
