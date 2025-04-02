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
python3 grading.py roster.csv questions.csv plots.pdf init
```

This will create the three following files:
- `roster.csv`: A CSV file containing the list of students, initially a single dummy student.
- `questions.csv`: A CSV file containing the list of questions, initially a single dummy question.
- `results.csv`: A CSV file containing the results of the grading, initially with 0.0 for the only cell.
- `plots.pdf`: A PDF file containing the plots for the questions, initially empty.

### Add students and questions

At any time, if the number of students or questions change, you may re-run the `init` command to re-generate the `results.csv` file. Note that this will overwrite the previous `results.csv` file, so make sure to back it up if needed.

### Add results

Once the roster and question set is correct, you may run the `watch` command to automatically re-generate the plots every time any of the csv files change.

```bash
python3 grading.py roster.csv questions.csv plots.pdf watch
```
