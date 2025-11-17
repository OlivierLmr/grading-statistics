import csv
import numpy as np
import sys
import time
import os
import matplotlib.pyplot as plt
import math
import json
from typing import Optional, List

# QUESTIONS


class Question:
    def __init__(self, part: str, title: str, points: float, coefficient: float):
        self.part = part
        self.title = title
        self.points = points
        self.coefficient = coefficient

    def __repr__(self):
        return f"Question(part='{self.part}', title='{self.title}', points={self.points}, coefficient={self.coefficient})"


def read_questions_from_csv(file_path: str):
    questions = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            part = row['part']
            title = row['name']
            points = float(row['points'])
            coefficient = float(row['coefficient'])
            questions.append(Question(part, title, points, coefficient))
    return questions


class Evaluation:
    def __init__(self, name: str, questions: list[Question]):
        self.name = name
        self.questions = questions

    def __repr__(self):
        return f"Evaluation(name='{self.name}', questions={self.questions})"

    def get_question_uid(self, question_number: int):
        if 0 <= question_number < len(self.questions):
            return f"Q{question_number + 1}"
        else:
            raise ValueError("Invalid question number")

    @classmethod
    def from_csv(cls, name: str, file_path: str):
        questions = read_questions_from_csv(file_path)
        return cls(name, questions)

    @staticmethod
    def create_sample_evaluation(file_path: str):
        sample_evaluation = [Question("Part 1", "Sample Question", 10.0, 1.0)]
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['part', 'name', 'points', 'coefficient']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for question in sample_evaluation:
                writer.writerow({
                    'part': question.part,
                    'name': question.title,
                    'points': question.points,
                    'coefficient': question.coefficient
                })
        print(f"Sample evaluation written to {file_path}")

# STUDENTS


class Student:
    def __init__(self, last_name: str, first_name: str, email: str):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email

    def __repr__(self):
        return f"Student(last_name='{self.last_name}', first_name='{self.first_name}', email='{self.email}')"


def read_students_from_csv(file_path: str):
    students = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            last_name = row['last name']
            first_name = row['first name']
            email = row['email']
            students.append(Student(last_name, first_name, email))
    return students


class Class:
    def __init__(self, name: str):
        self.name = name
        self.students = []

    def add_student(self, student: Student):
        self.students.append(student)

    def __repr__(self):
        return f"Class(name='{self.name}', students={self.students})"

    @classmethod
    def from_csv(cls, name: str, file_path: str):
        new_class = cls(name)
        students = read_students_from_csv(file_path)
        for student in students:
            new_class.add_student(student)
        return new_class

    @staticmethod
    def create_sample_class(file_path: str):
        sample_class = Class("Sample Class")
        sample_class.add_student(
            Student("Lemer", "Olivier", "olivier.lemer@example.com"))
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['last name', 'first name', 'email']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for student in sample_class.students:
                writer.writerow({
                    'last name': student.last_name,
                    'first name': student.first_name,
                    'email': student.email
                })
        print(f"Sample class written to {file_path}")

# SETTINGS


class GlobalSettings:
    def __init__(self, bonus_points: float = 0.0, added_points: float = 0.0, dropped_questions: Optional[List[int]] = None, given_questions: Optional[List[int]] = None):
        self.bonus_points = bonus_points
        self.added_points = added_points
        # Lists of question numbers (1-based) that are dropped or given
        self.dropped_questions = dropped_questions or []
        self.given_questions = given_questions or []

    def __repr__(self):
        return f"GlobalSettings(bonus={self.bonus_points}, added={self.added_points}, dropped={self.dropped_questions}, given={self.given_questions})"

    @classmethod
    def from_json(cls, file_path: str):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return cls(
                    bonus_points=data.get('bonus_points', 0.0),
                    added_points=data.get('added_points', 0.0),
                    dropped_questions=data.get('dropped_questions', []),
                    given_questions=data.get('given_questions', [])
                )
        else:
            return cls()

    def to_json(self, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'bonus_points': self.bonus_points,
                'added_points': self.added_points,
                'dropped_questions': self.dropped_questions,
                'given_questions': self.given_questions
            }, f, indent=4)


# Define a default instance of GlobalSettings as a class-level attribute
GlobalSettings.default = GlobalSettings(bonus_points=0.0)

# RESULTS

# Global constants for plot colors
HIGHLIGHT_COLOR = '#CC7722'  # Ocre color
SEC_HIGHLIGHT_COLOR = '#E6A96D'  # Lighter version of the primary color
PRIMARY_COLOR = 'gray'
SECONDARY_COLOR = 'gray'
TERNARY_COLOR = 'lightgray'


def round_up(x, digits):
    """Round a number up to the nearest multiple of 0.5."""
    return math.ceil(x * (10 ** digits)) / (10 ** digits)


assert (round_up(1.1, 1) == 1.1)
assert (round_up(1.11, 1) == 1.2)
assert (round_up(1.15, 1) == 1.2)
assert (round_up(1.19, 1) == 1.2)


class Results:
    def __init__(self, class_: Class, evaluation: Evaluation, settings: GlobalSettings = GlobalSettings.default):
        self.settings = settings
        self.class_ = class_
        self.evaluation = evaluation

        # Determine active questions by excluding dropped ones (dropped_questions are 1-based indices)
        active_indices = [i for i in range(len(evaluation.questions)) if (i + 1) not in getattr(self.settings, 'dropped_questions', [])]
        active_uids = [evaluation.get_question_uid(i) for i in active_indices]

        # Initialize scores only for active question UIDs
        self.scores = {student.email: {uid: 0.0 for uid in active_uids} for student in class_.students}

        # Apply 'given' questions: give full points to every student for those question numbers
        for qnum in getattr(self.settings, 'given_questions', []):
            idx = qnum - 1
            if 0 <= idx < len(evaluation.questions):
                uid = evaluation.get_question_uid(idx)
                # Only set if uid is active (i.e., not dropped)
                if uid in next(iter(self.scores.values()), {}):
                    full_score = evaluation.questions[idx].points
                    for student_email in self.scores:
                        self.scores[student_email][uid] = full_score

    # Helper methods to get active questions
    def active_question_indices(self):
        return [i for i in range(len(self.evaluation.questions)) if (i + 1) not in getattr(self.settings, 'dropped_questions', [])]

    def active_question_uids(self):
        return [self.evaluation.get_question_uid(i) for i in self.active_question_indices()]

    def get_question_by_index(self, i: int):
        return self.evaluation.questions[i]

    def get_score(self, student_email: str, question_number: int):
        if student_email in self.scores and 0 <= question_number < len(self.evaluation.questions):
            question_uid = self.evaluation.get_question_uid(question_number)
            if question_uid in self.scores[student_email]:
                return self.scores[student_email][question_uid]
            else:
                # Dropped question: behave as if it doesn't exist
                raise ValueError("Question has been dropped or does not exist for this results object")
        else:
            raise ValueError("Invalid student email or question number")

    def set_score(self, student_email: str, question_uid: str, score: float):
        if student_email in self.scores and question_uid in self.scores[student_email]:
            self.scores[student_email][question_uid] = score
        else:
            raise ValueError(
                f"Invalid student email or question UID: {student_email}, {question_uid}\nAvailable question UIDs are: {list(self.scores[student_email].keys())}")

    def calculate_student_score(self, student_email: str, clamp: bool = True):
        if student_email in self.scores:
            total = 0.0
            max_score = 0.0
            # Use only active questions for calculation
            for i in self.active_question_indices():
                question = self.evaluation.questions[i]
                question_uid = self.evaluation.get_question_uid(i)
                # score stored is raw points
                score = self.scores[student_email].get(question_uid, 0.0)
                total += score * question.coefficient
                max_score += question.points * question.coefficient
            total += self.settings.added_points
            grade = round_up((total / (max_score - self.settings.bonus_points)) * 5 + 1, 1) if max_score > 0 else 0.0
            if clamp:
                grade = min(grade, 6.0)
            return grade
        else:
            raise ValueError("Invalid student email")

    def __repr__(self):
        return f"Results(class_={self.class_.name}, evaluation={self.evaluation.name}, scores={self.scores})"

    def write_results_to_csv(self, file_path: str):
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            # Use only active question uids
            active_indices = self.active_question_indices()
            fieldnames = ['email'] + [self.evaluation.get_question_uid(i) for i in active_indices]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the part numbers as the first row
            part_row = {'email': 'Part'}
            part_row.update({self.evaluation.get_question_uid(i): self.evaluation.questions[i].part for i in active_indices})
            writer.writerow(part_row)

            # Write the question titles as the second row
            title_row = {'email': 'Title'}
            title_row.update({self.evaluation.get_question_uid(i): self.evaluation.questions[i].title for i in active_indices})
            writer.writerow(title_row)

            # Write the scores for each student
            writer.writeheader()
            for student_email, scores in self.scores.items():
                row = {'email': student_email}
                row.update({self.evaluation.get_question_uid(i): scores.get(self.evaluation.get_question_uid(i), 0.0) for i in active_indices})
                writer.writerow(row)

    def write_results_with_stats(self, file_path: str):
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            active_indices = self.active_question_indices()
            fieldnames = ['email'] + [self.evaluation.get_question_uid(i) for i in active_indices] + ['Total Grade']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the part numbers as the first row
            part_row = {'email': 'Part'}
            part_row.update({self.evaluation.get_question_uid(i): self.evaluation.questions[i].part for i in active_indices})
            writer.writerow(part_row)

            # Write the question titles as the second row
            title_row = {'email': 'Title'}
            title_row.update({self.evaluation.get_question_uid(i): self.evaluation.questions[i].title for i in active_indices})
            writer.writerow(title_row)

            # Write the scores for each student
            for student_email, scores in self.scores.items():
                row = {'email': student_email}
                row.update({self.evaluation.get_question_uid(i): scores.get(self.evaluation.get_question_uid(i), 0.0) for i in active_indices})
                row['Total Grade'] = self.calculate_student_score(student_email, clamp=False)
                writer.writerow(row)

            # Calculate and write the average for each question
            average_row = {'email': 'Average'}
            for i in active_indices:
                question_uid = self.evaluation.get_question_uid(i)
                question_scores = [self.scores[student_email].get(question_uid, 0.0) for student_email in self.scores]
                average_row[question_uid] = f"{np.mean(question_scores):.2f}" if question_scores else 0.0
            average_row['Total Grade'] = f"{self.get_total_average():.2f}"
            writer.writerow(average_row)

            # Calculate and write the median for each question
            median_row = {'email': 'Median'}
            for i in active_indices:
                question_uid = self.evaluation.get_question_uid(i)
                question_scores = [self.scores[student_email].get(question_uid, 0.0) for student_email in self.scores]
                median_row[question_uid] = np.median(question_scores) if question_scores else 0.0
            median_row['Total Grade'] = self.get_total_median()
            writer.writerow(median_row)

    @classmethod
    def read_results_from_csv(cls, file_path: str, class_: Class, evaluation: Evaluation, settings: GlobalSettings = GlobalSettings.default):
        # Initialize results with settings so dropped/given are taken into account
        results = cls(class_, evaluation, settings)
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)

            # Skip the first two rows (part and title rows)
            next(reader)
            next(reader)

            # Use the third row as the header
            headers = next(reader)
            question_uids = headers[1:]  # Exclude the 'email' column

            for row in reader:
                student_email = row[0]
                for i, question_uid in enumerate(question_uids):
                    # Only set scores for active questions (others are treated as dropped)
                    if student_email in results.scores and question_uid in results.scores[student_email]:
                        score = float(row[i + 1])
                        results.set_score(student_email, question_uid, score)

        # After reading, ensure that 'given' questions are set to full points for everyone
        for qnum in getattr(results.settings, 'given_questions', []):
            idx = qnum - 1
            if 0 <= idx < len(evaluation.questions):
                uid = evaluation.get_question_uid(idx)
                if uid in next(iter(results.scores.values()), {}):
                    full_score = evaluation.questions[idx].points
                    for student_email in results.scores:
                        results.scores[student_email][uid] = full_score

        return results

    def plot_style(self, ax):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(TERNARY_COLOR)
        ax.spines['bottom'].set_color(TERNARY_COLOR)
        ax.yaxis.tick_left()
        ax.xaxis.tick_bottom()
        ax.tick_params(axis='x', colors=SECONDARY_COLOR)
        ax.tick_params(axis='y', colors=SECONDARY_COLOR)

    def plot_grades_histogram(self, ax, bin_width: float = 0.5):
        grades = [self.calculate_student_score(
            student.email) for student in self.class_.students]
        bins = [i * bin_width for i in range(int(6 / bin_width) + 1)]

        self.plot_style(ax)

        ax.hist(grades, bins=bins, color=SEC_HIGHLIGHT_COLOR,
                rwidth=0.8, zorder=2)
        ax.set_title('Histogram of Grades')
        ax.set_xlabel('Grades')
        ax.set_ylabel('Number of Students')
        ax.set_xticks(bins)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    def plot_statistics(self, ax, labels, max_points, min_values, q1_values, median_values, q3_values, max_values, average_values):
        # Plotting
        x_positions = np.arange(len(labels))

        quartiles_handle = None
        min_handle = None
        max_handle = None
        median_handle = None
        max_points_handle = None

        self.plot_style(ax)

        for i, (min_val, q1, median, q3, max_val, max_point) in enumerate(zip(min_values, q1_values, median_values, q3_values, max_values, max_points)):
            # Vertical dashed line from min to max
            ax.plot([i, i], [min_val, max_val], color='gray',
                    linestyle='--', linewidth=1, zorder=1)
            # Line at min
            min_handle, = ax.plot(
                [i - 0.2, i + 0.2], [min_val, min_val], color=SECONDARY_COLOR, linewidth=1, zorder=3)
            # Line at max
            max_handle, = ax.plot(
                [i - 0.2, i + 0.2], [max_val, max_val], color=SECONDARY_COLOR, linewidth=1, zorder=3)

            # Box between Q1 and Q3
            quartiles_handle, = ax.bar(
                i, q3 - q1, bottom=q1, width=0.4, color=SEC_HIGHLIGHT_COLOR, zorder=2)
            # Line at median
            median_handle, = ax.plot(
                [i - 0.2, i + 0.2], [median, median], color=HIGHLIGHT_COLOR, linewidth=2, zorder=3)

            # Lightgray bar in the background for max obtainable points
            max_points_handle, = ax.bar(
                i, max_point, width=0.8, color=TERNARY_COLOR, alpha=0.5, zorder=0)

            # Average values
            average_handle = ax.bar(
                i, average_values[i], width=0.8, color=HIGHLIGHT_COLOR, alpha=0.2, zorder=0)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_ylabel('Scores')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        # ax.legend([max_points_handle, max_handle, quartiles_handle, average_handle, median_handle, min_handle],
        #   ['Max Points', 'Max', 'Q1-Q3 Range', 'Average', 'Median', 'Min'], loc='upper right')

    def plot_question_statistics(self, ax):
        # Calculate statistics per question
        question_titles = []
        # Use only active questions
        active_indices = self.active_question_indices()
        max_points = [self.evaluation.questions[i].points * self.evaluation.questions[i].coefficient for i in active_indices]
        min_values = []
        q1_values = []
        median_values = []
        average_values = []
        q3_values = []
        max_values = []

        last_part = None
        part_id = 0

        for i in active_indices:
            question = self.evaluation.questions[i]
            question_uid = self.evaluation.get_question_uid(i)
            question_scores = [self.scores[student_email].get(question_uid, 0.0) * question.coefficient for student_email in self.scores]

            if question.part != last_part:
                last_part = question.part
                part_id += 1
                question_titles.append(f"{question.part} : {question.title}")
            else:
                question_titles.append(f"{question.title}")

            if question_scores:
                quartiles = np.percentile(question_scores, [0, 25, 50, 75, 100])
                min_values.append(quartiles[0])
                q1_values.append(quartiles[1])
                median_values.append(quartiles[2])
                q3_values.append(quartiles[3])
                max_values.append(quartiles[4])
                average_values.append(np.mean(question_scores))

        self.plot_statistics(ax, question_titles, max_points, min_values,
                             q1_values, median_values, q3_values, max_values, average_values)
        ax.set_title('Statistics per Question')

    def plot_statistics_per_part(self, ax):
        # Group questions by part
        parts = {}
        active_indices = self.active_question_indices()
        for i in active_indices:
            question = self.evaluation.questions[i]
            question_uid = self.evaluation.get_question_uid(i)
            if question.part not in parts:
                parts[question.part] = []
            parts[question.part].append((question, question_uid))

        # Calculate statistics per part
        part_titles = []
        max_points = []
        max_values = []
        q1_values = []
        median_values = []
        q3_values = []
        min_values = []
        average_values = []

        for part, questions in parts.items():
            part_scores = [0 for _ in range(len(self.scores))]
            part_max_points = sum(
                question.points * question.coefficient for question, _ in questions)

            for question, question_uid in questions:
                for i, student_email in enumerate(self.scores):
                    part_scores[i] += self.scores[student_email].get(question_uid, 0.0) * question.coefficient

            if part_scores:
                quartiles = np.percentile(part_scores, [0, 25, 50, 75, 100])
                part_titles.append(part)
                max_points.append(part_max_points)
                max_values.append(quartiles[4])
                min_values.append(quartiles[0])
                q1_values.append(quartiles[1])
                median_values.append(quartiles[2])
                q3_values.append(quartiles[3])
                average_values.append(np.mean(part_scores))

        self.plot_statistics(ax, part_titles, max_points, min_values,
                             q1_values, median_values, q3_values, max_values, average_values)
        ax.set_title('Statistics per Part')

    def plot_average_and_max_per_question(self, ax):
        active_indices = self.active_question_indices()
        question_uids = [self.evaluation.get_question_uid(i) for i in active_indices]
        max_grades = [self.evaluation.questions[i].points for i in active_indices]

        # Calculate average grades for each question
        average_grades = []
        for i, uid in zip(active_indices, question_uids):
            total_score = sum(self.scores[student_email].get(uid, 0.0) for student_email in self.scores)
            average_grades.append(total_score / len(self.scores) if self.scores else 0)

        self.plot_average_and_max(
            ax, [self.evaluation.questions[i].title for i in active_indices], average_grades, max_grades)

    def plot_average_and_max_grades_per_part(self, ax):
        # Group questions by part
        parts = {}
        active_indices = self.active_question_indices()
        for i in active_indices:
            question = self.evaluation.questions[i]
            question_uid = self.evaluation.get_question_uid(i)
            if question.part not in parts:
                parts[question.part] = []
            parts[question.part].append((question, question_uid))

        # Calculate average and max grades per part
        part_titles = list(parts.keys())
        max_grades = []
        average_grades = []

        for part, questions in parts.items():
            part_max_grade = sum(question.points for question, _ in questions)
            part_total_score = 0.0
            for question, question_uid in questions:
                part_total_score += sum(self.scores[student_email].get(question_uid, 0.0)
                                        for student_email in self.scores)
            part_average_grade = part_total_score / \
                len(self.scores) if self.scores else 0.0
            max_grades.append(part_max_grade)
            average_grades.append(part_average_grade)

        self.plot_average_and_max(ax, part_titles, average_grades, max_grades)

    def plot_global_statistics_h(self, ax, show_individual: bool = True):
        # Plot overall statistics in the 6th subplot
        all_grades = [self.calculate_student_score(
            student.email) for student in self.class_.students]
        quartiles = np.percentile(all_grades, [0, 25, 50, 75, 100])
        average_grade = np.mean(all_grades)

        self.plot_style(ax)

        # Light box in the background for the full grade range
        ax.barh(0, 6, left=0, height=0.4,
                color=TERNARY_COLOR, alpha=0.5, zorder=0)

        # Box between Q1 and Q3
        quartiles_handle, = ax.barh(
            0, quartiles[3] - quartiles[1], left=quartiles[1], height=0.2, color=SEC_HIGHLIGHT_COLOR, zorder=2)

        # Line at value 4
        ax.plot([4, 4], [-0.4, 0.4], color=SECONDARY_COLOR,
                linestyle='--', linewidth=1, zorder=1)

        # Line at median
        median_handle, = ax.plot([quartiles[2], quartiles[2]],
                                 [-0.1, 0.1], color=HIGHLIGHT_COLOR, linewidth=2, zorder=3)

        # Line at average
        avg_handle = ax.barh(0, average_grade, height=0.4,
                             color=HIGHLIGHT_COLOR, alpha=0.2, zorder=0)

        # Line at min
        ax.plot([quartiles[0], quartiles[0]], [-0.1, 0.1],
                color=SECONDARY_COLOR, linewidth=1, zorder=3)

        # Line at max
        ax.plot([quartiles[4], quartiles[4]], [-0.1, 0.1],
                color=SECONDARY_COLOR, linewidth=1, zorder=3)

        # Scatter plot of all grades
        if show_individual:
            all_grades = [self.calculate_student_score(
                student.email) for student in self.class_.students]
            np.random.seed(0)  # For reproducibility
            y_offsets_amp = 0.03
            y_offsets = np.random.uniform(-y_offsets_amp,
                                          y_offsets_amp, len(all_grades))
            ax.scatter(all_grades, y_offsets, color=HIGHLIGHT_COLOR, zorder=4)

        # Dashed line from min to max
        minmax_handle, = ax.plot([quartiles[0], quartiles[4]], [
                                 0, 0], color=SECONDARY_COLOR, linestyle='--', linewidth=1, zorder=1)

        ax.set_title('Overall Grade Statistics')
        ax.set_xlabel('Grades')
        ax.set_yticks([])
        ax.legend([minmax_handle, avg_handle, median_handle, quartiles_handle],
                  ['Min to Max', 'Average', 'Median', 'Q1-Q3 Range', 'Min'], loc='upper left')
        ax.grid(axis='x', linestyle='--', alpha=0.7)

    def plot_global_statistics_v(self, ax, show_individual: bool = True):
        # Plot overall statistics vertically
        all_grades = [self.calculate_student_score(
            student.email) for student in self.class_.students]
        quartiles = np.percentile(all_grades, [0, 25, 50, 75, 100])
        average_grade = np.mean(all_grades)

        self.plot_style(ax)

        # Light box in the background for the full grade range
        ax.bar(0, 6, bottom=0, width=0.4,
               color=TERNARY_COLOR, alpha=0.5, zorder=0)

        # Box between Q1 and Q3
        quartiles_handle, = ax.bar(
            0, quartiles[3] - quartiles[1], bottom=quartiles[1], width=0.2, color=SEC_HIGHLIGHT_COLOR, zorder=2)

        # Line at value 4
        ax.plot([-0.5, 0.5], [4, 4], color=SECONDARY_COLOR,
                linestyle='--', linewidth=1, zorder=1)

        # Line at median
        median_handle, = ax.plot(
            [-0.1, 0.1], [quartiles[2], quartiles[2]], color=HIGHLIGHT_COLOR, linewidth=2, zorder=3)

        # Line at average
        avg_handle = ax.bar(0, average_grade, width=0.4,
                            color=HIGHLIGHT_COLOR, alpha=0.2, zorder=0)

        # Line at min
        ax.plot([-0.1, 0.1], [quartiles[0], quartiles[0]],
                color=SECONDARY_COLOR, linewidth=1, zorder=3)

        # Line at max
        ax.plot([-0.1, 0.1], [quartiles[4], quartiles[4]],
                color=SECONDARY_COLOR, linewidth=1, zorder=3)

        # Dashed line from min to max
        minmax_handle, = ax.plot([0, 0], [quartiles[0], quartiles[4]],
                                 color=SECONDARY_COLOR, linestyle='--', linewidth=1, zorder=1)

        if show_individual:

            # Scatter plot of all grades
            all_grades = [self.calculate_student_score(
                student.email) for student in self.class_.students]
            np.random.seed(0)  # For reproducibility
            x_offsets_amp = 0.03
            x_offsets = np.random.uniform(-x_offsets_amp,
                                          x_offsets_amp, len(all_grades))
            ax.scatter(x_offsets, all_grades, color=HIGHLIGHT_COLOR, zorder=6)

            # Add student names to the right of the plot with lines connecting to points
            offset = 1000
            min_gap = 0.15
            x_pos = 0.51
            # Sort students by descending grade and align x_offsets accordingly
            student_offsets = list(zip(self.class_.students, x_offsets))
            sorted_student_offsets = sorted(
                student_offsets, key=lambda pair: self.calculate_student_score(pair[0].email), reverse=True)

            for i, (student, x_offset) in enumerate(sorted_student_offsets):
                grade = self.calculate_student_score(student.email)
                offset = min(offset - min_gap, grade)
                ax.text(x_pos, offset, f"{grade} {student.first_name} {student.last_name}",
                        fontsize=8, color=PRIMARY_COLOR, va='center')
                ax.plot([x_offset, x_pos], [grade, offset], color="black",
                        alpha=0.2, linestyle='-', linewidth=0.5, zorder=5)

            # Adjust the grid to stop at around 1 on the right
            ax.set_xlim(left=-0.5, right=0.5)

        ax.set_title('Overall Grade Statistics')
        ax.set_ylabel('Grades')
        ax.set_xticks([])
        ax.legend([minmax_handle, avg_handle, median_handle, quartiles_handle],
                  ['Min to Max', 'Average', 'Median', 'Q1-Q3 Range'], loc='lower left')
        ax.grid(axis='y', linestyle='--', alpha=0.7, clip_on=False)

    def plot_global_statistics_split(self, ax):
        ax.axis('off')  # Turn off the axis

        # Split the ax into two subplots locally
        left_ax = ax.inset_axes([0, 0, 0.5, 1])  # Left half
        right_ax = ax.inset_axes([0.5, 0, 0.5, 1])  # Right half

        # Plot global statistics vertically on the left subplot
        self.plot_global_statistics_v(left_ax)

        # Leave the right subplot empty or add additional content if needed
        right_ax.axis('off')  # Turn off the right subplot for now

    def get_total_average(self):
        all_grades = [self.calculate_student_score(
            student.email) for student in self.class_.students]
        return np.average(all_grades) if all_grades else 0.0

    def get_total_max(self):
        all_grades = [self.calculate_student_score(
            student.email) for student in self.class_.students]
        return max(all_grades) if all_grades else 0.0

    def get_total_min(self):
        all_grades = [self.calculate_student_score(
            student.email) for student in self.class_.students]
        return min(all_grades) if all_grades else 0.0

    def get_total_median(self):
        all_grades = [self.calculate_student_score(
            student.email) for student in self.class_.students]
        return np.median(all_grades) if all_grades else 0.0

    def get_count_below_4(self):
        count = 0
        for student_email in self.scores:
            if self.calculate_student_score(student_email) < 4:
                count += 1
        return count

    def get_percent_below_4(self):
        count = self.get_count_below_4()
        total_students = len(self.class_.students)
        return (count / total_students) * 100 if total_students > 0 else 0.0

    def write_global_values(self, ax, show_individual: bool = True):
        ax.axis('off')  # Turn off the axis
        text = f"Average: {self.get_total_average():.2f}\n" + \
            f"Median: {self.get_total_median():.2f}\n" + \
            f"Max: {self.get_total_max():.2f}\n" + \
            f"Min: {self.get_total_min():.2f}\n" + \
            f"{self.get_count_below_4()}/{len(self.class_.students)} students ({self.get_percent_below_4():.2f}%) below 4.\n"
        ax.text(0, 0.5, text, transform=ax.transAxes, ha='left',
                va='center', fontsize=14, color=PRIMARY_COLOR, linespacing=1.5)

    def plot_all_statistics(self, file_path: str, show_individual: bool = True):
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, height_ratios=[
                              4, 3, 1], width_ratios=[1, 1, 0.4])

        # First row: Statistics per part
        ax1 = fig.add_subplot(gs[0, 0])
        self.plot_statistics_per_part(ax1)

        # Second row: Statistics per question (spans two rows)
        ax2 = fig.add_subplot(gs[1:, 0:2])
        self.plot_question_statistics(ax2)

        # Second row, second column: Histogram
        ax3 = fig.add_subplot(gs[0, 1])
        self.plot_grades_histogram(ax3)

        # Third row, second column: Global Statistics
        ax4 = fig.add_subplot(gs[:2, 2])
        self.plot_global_statistics_v(ax4, show_individual)

        # Add some text to the lower-right ax
        ax5 = fig.add_subplot(gs[2, 2])
        self.write_global_values(ax5, show_individual)

        plt.tight_layout()
        plt.savefig(file_path)
        plt.close(fig)


def main():
    if len(sys.argv) != 3:
        print("Usage: python planning.py <folder_path> <command>")
        sys.exit(1)

    folder_path = sys.argv[1]
    command = sys.argv[2]

    roster_file = os.path.join(folder_path, "roster.csv")
    questions_file = os.path.join(folder_path, "questions.csv")
    plots_file = os.path.join(folder_path, "plots.pdf")
    settings_file = os.path.join(folder_path, "settings.json")
    results_file = os.path.join(folder_path, "results.csv")

    if command not in ['init', 'watch']:
        print("Command must be either 'init' or 'watch'")
        sys.exit(1)

    class_name = "Class"
    evaluation_name = "Evaluation"

    if command == 'init':
        settings = GlobalSettings()

        # Create the folder if it does not exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")

        # Create dummy evaluation and class CSVs if they don't exist
        if not os.path.exists(roster_file):
            Class.create_sample_class(roster_file)
        if not os.path.exists(questions_file):
            Evaluation.create_sample_evaluation(questions_file)
        if not os.path.exists(settings_file):
            settings.to_json(settings_file)

        # Initialize class and evaluation
        class_ = Class.from_csv(class_name, roster_file)
        evaluation = Evaluation.from_csv(evaluation_name, questions_file)
        results = Results(class_, evaluation, settings)

        # Save initial results to a CSV file
        results.write_results_to_csv(results_file)
        print(f"Initialized results and saved to {results_file}")

    elif command == 'watch':
        # Watch for changes in the results file
        if not os.path.exists(results_file):
            print(
                f"Results file '{results_file}' does not exist. Run 'init' first.")
            sys.exit(1)

        class_ = Class.from_csv(class_name, roster_file)
        evaluation = Evaluation.from_csv(evaluation_name, questions_file)

        print(
            f"Watching for changes in {results_file}, {roster_file}, and {questions_file}...")
        last_modified_times = {
            'results': os.path.getmtime(results_file),
            'roster': os.path.getmtime(roster_file),
            'questions': os.path.getmtime(questions_file),
            'settings': os.path.getmtime(settings_file)
        }

        try:
            first_run = True
            while True:

                current_modified_times = {
                    'results': os.path.getmtime(results_file),
                    'roster': os.path.getmtime(roster_file),
                    'questions': os.path.getmtime(questions_file),
                    'settings': os.path.getmtime(settings_file)
                }

                settings = GlobalSettings.from_json(settings_file)

                for file_type, last_modified_time in last_modified_times.items():
                    if current_modified_times[file_type] == last_modified_time and not first_run:
                        continue

                    first_run = False

                    print(
                        f"{file_type.capitalize()} file has been updated (was {last_modified_time}, now {current_modified_times[file_type]})")

                    # Reload class or evaluation if necessary
                    if file_type == 'roster':
                        class_ = Class.from_csv(class_name, roster_file)
                    elif file_type == 'questions':
                        evaluation = Evaluation.from_csv(
                            evaluation_name, questions_file)

                    # Reload results and update plots
                    results = Results.read_results_from_csv(
                        results_file, class_, evaluation, settings)
                    results.plot_all_statistics(plots_file)
                    anonym_plots_file = os.path.splitext(
                        plots_file)[0] + '_anonym' + os.path.splitext(plots_file)[1]
                    results.plot_all_statistics(
                        anonym_plots_file, show_individual=False)
                    results.write_results_with_stats(os.path.splitext(
                        results_file)[0] + '_with_stats' + os.path.splitext(results_file)[1])
                    print(f"Plots updated and saved to {plots_file}")

                    # Update the last modified time
                    last_modified_times[file_type] = current_modified_times[file_type]

                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopped watching.")


if __name__ == "__main__":
    main()
