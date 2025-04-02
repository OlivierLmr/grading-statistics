import csv
import numpy as np
import sys
import time
import os
import matplotlib.pyplot as plt

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
        sample_class.add_student(Student("Lemer", "Olivier", "olivier.lemer@example.com"))
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

        
# RESULTS
    
class Results:
    def __init__(self, class_: Class, evaluation: Evaluation):
        self.class_ = class_
        self.evaluation = evaluation
        self.scores = {student.email: {question.title: 0.0 for question in evaluation.questions} for student in class_.students}

    def get_score(self, student_email: str, question_number: int):
        if student_email in self.scores and 0 <= question_number < len(self.evaluation.questions):
            question_title = self.evaluation.questions[question_number].title
            return self.scores[student_email][question_title]
        else:
            raise ValueError("Invalid student email or question number")

    def set_score(self, student_email: str, question_title: str, score: float):
        if student_email in self.scores and question_title in self.scores[student_email]:
            self.scores[student_email][question_title] = score
        else:
            raise ValueError(f"Invalid student email or question title: {student_email}, {question_title}\n")

    def calculate_student_score(self, student_email: str):
        if student_email in self.scores:
            total = 0.0
            max_score = 0.0
            for question in self.evaluation.questions:
                total += self.scores[student_email][question.title] * question.coefficient
                max_score += question.points * question.coefficient
            return (total / max_score) * 5 + 1 if max_score > 0 else 0.0
        else:
            raise ValueError("Invalid student email")

    def __repr__(self):
        return f"Results(class_={self.class_.name}, evaluation={self.evaluation.name}, scores={self.scores})"
    
    def write_results_to_csv(self, file_path: str):
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['email'] + [f"Q{i+1}" for i in range(len(self.evaluation.questions))]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for student_email, scores in self.scores.items():
                row = {'email': student_email}
                row.update({f"Q{i+1}": scores[question.title] for i, question in enumerate(self.evaluation.questions)})
                writer.writerow(row)

    @classmethod
    def read_results_from_csv(cls, file_path: str, class_: Class, evaluation: Evaluation):
        results = cls(class_, evaluation)
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                student_email = row['email']
                for i, question in enumerate(evaluation.questions):
                    question_title = question.title
                    score = float(row[f"Q{i+1}"])
                    results.set_score(student_email, question_title, score)
        return results
    
    def plot_grades_histogram(self, ax, bin_width: float = 0.5):
        grades = [self.calculate_student_score(student.email) for student in self.class_.students]
        bins = [i * bin_width for i in range(int(6 / bin_width) + 1)]
        ax.hist(grades, bins=bins, edgecolor='black')
        ax.set_title('Histogram of Grades')
        ax.set_xlabel('Grades')
        ax.set_ylabel('Number of Students')
        ax.set_xticks(bins)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    def plot_question_statistics(self, ax):
        question_titles = [question.title for question in self.evaluation.questions]
        max_grades = [question.points for question in self.evaluation.questions]

        question_scores = {title: [] for title in question_titles}
        for student_email in self.scores:
            for question in self.evaluation.questions:
                question_scores[question.title].append(self.scores[student_email][question.title])

        positions = np.arange(len(question_titles))

        # Boxplot for quartiles
        data = [question_scores[title] for title in question_titles]
        ax.boxplot(data, positions=positions, widths=0.6, patch_artist=True, boxprops=dict(facecolor="lightblue"))

        # Plot max attainable grades
        ax.scatter(positions, max_grades, color='red', label='Max Grade', zorder=3)

        ax.set_xticks(positions)
        ax.set_xticklabels(question_titles, rotation=45, ha='right')
        ax.set_title('Question Statistics')
        ax.set_ylabel('Grades')
        ax.set_xlabel('Questions')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    def plot_average_and_max_grades(self, ax):
        question_titles = [question.title for question in self.evaluation.questions]
        max_grades = [question.points for question in self.evaluation.questions]

        # Calculate average grades for each question
        average_grades = []
        for question in self.evaluation.questions:
            total_score = sum(self.scores[student_email][question.title] for student_email in self.scores)
            average_grades.append(total_score / len(self.scores) if self.scores else 0)

        # Plotting
        x_positions = np.arange(len(question_titles))
        width = 0.4

        ax.bar(x_positions - width / 2, average_grades, width, label='Average Grade', color='skyblue')
        ax.bar(x_positions + width / 2, max_grades, width, label='Max Grade', color='orange')

        ax.set_xticks(x_positions)
        ax.set_xticklabels(question_titles, rotation=45, ha='right')
        ax.set_title('Average and Max Grades per Question')
        ax.set_ylabel('Grades')
        ax.set_xlabel('Questions')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    def plot_statistics_per_part(self, ax):
        # Group questions by part
        parts = {}
        for question in self.evaluation.questions:
            if question.part not in parts:
                parts[question.part] = []
            parts[question.part].append(question)

        # Calculate average and max grades per part
        part_titles = list(parts.keys())
        max_grades = []
        average_grades = []

        for part, questions in parts.items():
            part_max_grade = sum(question.points for question in questions)
            part_total_score = 0.0
            for question in questions:
                part_total_score += sum(self.scores[student_email][question.title] for student_email in self.scores)
            part_average_grade = part_total_score / len(self.scores) if self.scores else 0.0
            max_grades.append(part_max_grade)
            average_grades.append(part_average_grade)

        # Plotting
        x_positions = np.arange(len(part_titles))
        bar_width = 0.6

        # Plot max grades as bars
        ax.bar(x_positions, max_grades, bar_width, label='Max Grade', color='orange', alpha=0.5)

        # Plot average grades as scatter points on top of the bars
        ax.scatter(x_positions, average_grades, color='blue', label='Average Grade', zorder=3)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(part_titles, rotation=45, ha='right')
        ax.set_title('Average and Max Grades per Part')
        ax.set_ylabel('Grades')
        ax.set_xlabel('Parts')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    def plot_all_statistics(self, file_path: str):
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        self.plot_grades_histogram(axes[0, 0])
        self.plot_statistics_per_part(axes[0, 1])
        self.plot_question_statistics(axes[1, 0])
        self.plot_average_and_max_grades(axes[1, 1])

        plt.tight_layout()
        plt.savefig(file_path)
        plt.close(fig)
        
def main():
    if len(sys.argv) != 5:
        print("Usage: python planning.py <roster_file> <questions_file> <plots_file> <command>")
        sys.exit(1)

    roster_file = sys.argv[1]
    questions_file = sys.argv[2]
    plots_file = sys.argv[3]
    command = sys.argv[4]

    if command not in ['init', 'watch']:
        print("Command must be either 'init' or 'watch'")
        sys.exit(1)

    class_name = "Class"
    evaluation_name = "Evaluation"

    if command == 'init':
        # Create dummy evaluation and class CSVs if they don't exist
        if not os.path.exists(roster_file):
            Class.create_sample_class(roster_file)
        if not os.path.exists(questions_file):
            Evaluation.create_sample_evaluation(questions_file)

        # Initialize class and evaluation
        class_ = Class.from_csv(class_name, roster_file)
        evaluation = Evaluation.from_csv(evaluation_name, questions_file)
        results = Results(class_, evaluation)

        # Save initial results to a CSV file
        results_file = "results.csv"
        results.write_results_to_csv(results_file)
        print(f"Initialized results and saved to {results_file}")

    elif command == 'watch':
        # Watch for changes in the results file
        results_file = "results.csv"
        if not os.path.exists(results_file):
            print(f"Results file '{results_file}' does not exist. Run 'init' first.")
            sys.exit(1)

        class_ = Class.from_csv(class_name, roster_file)
        evaluation = Evaluation.from_csv(evaluation_name, questions_file)

        print(f"Watching for changes in {results_file}, {roster_file}, and {questions_file}...")
        last_modified_times = {
            'results': os.path.getmtime(results_file),
            'roster': os.path.getmtime(roster_file),
            'questions': os.path.getmtime(questions_file)
        }

        try:
            first_run = True
            while True:

                current_modified_times = {
                    'results': os.path.getmtime(results_file),
                    'roster': os.path.getmtime(roster_file),
                    'questions': os.path.getmtime(questions_file)
                }

                for file_type, last_modified_time in last_modified_times.items():
                    if current_modified_times[file_type] == last_modified_time and not first_run:
                        continue

                    first_run = False

                    print(f"{file_type.capitalize()} file has been updated (was {last_modified_time}, now {current_modified_times[file_type]})")
                    
                    # Reload class or evaluation if necessary
                    if file_type == 'roster':
                        class_ = Class.from_csv(class_name, roster_file)
                    elif file_type == 'questions':
                        evaluation = Evaluation.from_csv(evaluation_name, questions_file)

                    # Reload results and update plots
                    results = Results.read_results_from_csv(results_file, class_, evaluation)
                    results.plot_all_statistics(plots_file)
                    print(f"Plots updated and saved to {plots_file}")

                    # Update the last modified time
                    last_modified_times[file_type] = current_modified_times[file_type]

                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nStopped watching.")

if __name__ == "__main__":
    main()
