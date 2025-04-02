import csv
import numpy as np
import sys
import time
import os
import matplotlib.pyplot as plt

# QUESTIONS

class Question:
    def __init__(self, title: str, points: float, coefficient: float):
        self.title = title
        self.points = points
        self.coefficient = coefficient

    def __repr__(self):
        return f"Question(title='{self.title}', points={self.points}, coefficient={self.coefficient})"

def read_questions_from_csv(file_path: str):
    questions = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['name']
            points = float(row['points'])
            coefficient = float(row['coefficient'])
            questions.append(Question(title, points, coefficient))
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

    def plot_all_statistics(self, file_path: str):
        fig, axes = plt.subplots(3, 1, figsize=(10, 18))

        self.plot_grades_histogram(axes[0])
        self.plot_question_statistics(axes[1])
        self.plot_average_and_max_grades(axes[2])

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

        print(f"Watching for changes in {results_file}...")
        last_modified_time = os.path.getmtime(results_file)

        try:
            while True:
                current_modified_time = os.path.getmtime(results_file)
                if current_modified_time != last_modified_time:
                    print(f"{results_file} has been updated.")
                    results = Results.read_results_from_csv(results_file, class_, evaluation)
                    results.plot_all_statistics(plots_file)
                    print(f"Plots updated and saved to {plots_file}")
                    last_modified_time = current_modified_time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped watching.")

if __name__ == "__main__":
    main()
