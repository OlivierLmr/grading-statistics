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

Run the program with a single argument: the folder that will contain (or already contains) the grading files.

```bash
python3 grading.py folder_name
```

Behavior:
- If the folder or any required files (roster.csv, questions.csv, settings.json, results.csv) are missing or incomplete, the program will report what is missing and ask for your consent to initialize the folder. If you consent it will:
  - create the folder if needed,
  - write sample `roster.csv` and `questions.csv` if they are missing,
  - write a `settings.json` file containing all supported settings with their default values if missing,
  - write an initial `results.csv` (with 0.0 scores) and exit the initialization step.
- If you decline initialization the program exits.
- When the required files are present the program runs a watcher loop: it monitors `results.csv`, `roster.csv`, `questions.csv` and `settings.json`. On any change it regenerates:
  - `plots.pdf` (detailed plots),
  - `plots_anonym.pdf` (anonymized plots without individual names),
  - `results_with_stats.csv` (results plus total grade and per-question statistics).

Notes on CSV layout and plotting:
- The program treats question numbers as 1-based (Q1, Q2, ...), in the order they appear in `questions.csv`.
- Question numbers are now prefixed to question titles in plots and labels (e.g. "Q1 Question title").
- If a question is listed in `dropped_questions` in settings.json it is treated as if it never existed: it is excluded from calculations, CSV outputs and plots.
- If a question is listed in `given_questions` every student is awarded the full points for that question (unless it is also dropped).

### Files created by initialization
- `roster.csv` — list of students (columns: last name, first name, email).
- `questions.csv` — list of questions (columns: part, name, points, coefficient).
- `results.csv` — per-student per-question scores (first two rows contain part and title rows, followed by a header row and student rows).
- `settings.json` — contains all supported settings (see below) with default values.

### Default settings.json (written by init)
When the program creates a default `settings.json` it will include all supported fields with sensible defaults. Example default content:

```json
{
    "bonus_points": 0.0,
    "added_points": 0.0,
    "dropped_questions": [],
    "given_questions": []
}
```

(You can edit `settings.json` at any time; changes will be picked up by the watcher.)

### Add students, questions or edit results
- To add students or questions, edit `roster.csv` and `questions.csv` respectively.
- If you change the number of questions you may need to re-run the program and allow initialization to re-create a matching `results.csv` (or update `results.csv` manually to match the new questions layout).

### Add results and run the watcher
- After files are present, run:

```bash
python3 grading.py folder_name
```

The program will watch for changes and automatically regenerate `plots.pdf`, `plots_anonym.pdf` and `results_with_stats.csv` whenever `results.csv`, `roster.csv`, `questions.csv` or `settings.json` are modified.
