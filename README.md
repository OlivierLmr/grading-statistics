# Grading Project

## Description
This project is designed to assist with grading tasks by providing tools and automation to streamline the process.

## Installation
Might need to use a python virtual environment, as follows:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

### Generate files

First run the init command to generate all necessary files :

```bash
python3 grading.py folder_name init
```

This will create a folder named `folder_name` in the current directory. Inside this folder, it will create the following files:

- `roster.csv`: A CSV file containing the list of students, initially a single dummy student.
- `questions.csv`: A CSV file containing the list of questions, initially a single dummy question.
- `results.csv`: A CSV file containing the results of the grading, initially with 0.0 for the only cell.
- `settings.json`: A JSON file containing the settings for the grading process, e.g. bonus points.

### Settings (all supported fields)

The project supports the following fields in `settings.json`. All are optional; sensible defaults are used when a field is missing.

- `bonus_points` (number, default 0.0)
  - Reduces the effective maximum score used when converting total points to the grade scale. Internally the grade formula divides by (max_score - bonus_points). Use with care: a positive value decreases the denominator and therefore raises grades.

- `added_points` (number, default 0.0)
  - Added to each student's total points before converting to the grade scale. Use this to give everyone the same extra points.

- `dropped_questions` (array of integers, default [])
  - A list of 1-based question numbers to ignore entirely. Dropped questions are excluded from all calculations, CSV outputs and plots (they are treated as if they never existed in the evaluation).

- `given_questions` (array of integers, default [])
  - A list of 1-based question numbers to grant full points to every student. Values in `results.csv` for these questions are ignored and every student will receive the question's maximum points.

Behavior notes:
- Indexing is 1-based and matches the order in `questions.csv` (Q1, Q2, ...).
- If a question is listed in both `dropped_questions` and `given_questions`, it will be dropped (ignored).
- When `settings.json` changes while the `watch` command is running, the watcher will reload settings and regenerate plots and the _with_stats CSV.
- The `init` command writes a `settings.json` with default values if none exists; you can edit it afterwards.

Example `settings.json` (full):

```json
{
    "bonus_points": 1.0,
    "added_points": 0.5,
    "dropped_questions": [3],
    "given_questions": [1, 2]
}
```

### Add students and questions

At any time, if the number of students or questions change, you may re-run the `init` command to re-generate the `results.csv` file. Note that this will overwrite the previous `results.csv` file, so make sure to back it up if needed.

### Add results

Once the roster and question set is correct, you may run the `watch` command. This will automatically re-generate a `plots.pdf` file in the provided folder every time any of the csv files changes.

```bash
python3 grading.py folder_name watch
```
