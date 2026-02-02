"""
Unit tests for Results class statistics methods.

Tests the statistical calculation methods: average, median, min, max,
and percentage calculations.
"""
import pytest
from grading import Results, GlobalSettings


@pytest.mark.unit
class TestResultsStatistics:
    """Tests for Results statistics methods."""

    @pytest.fixture
    def results_with_grades(self, sample_class, sample_evaluation, sample_settings):
        """Create a results instance with predefined scores."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        # Student 1: 40/50 points -> grade ~5.0
        results.set_score("john.doe@example.com", "Q1", 8.0)   # out of 10
        results.set_score("john.doe@example.com", "Q2", 12.0)  # out of 15
        results.set_score("john.doe@example.com", "Q3", 16.0)  # out of 20
        results.set_score("john.doe@example.com", "Q4", 4.0)   # out of 5

        # Student 2: 25/50 points -> grade = 3.5
        results.set_score("jane.smith@example.com", "Q1", 5.0)
        results.set_score("jane.smith@example.com", "Q2", 7.5)
        results.set_score("jane.smith@example.com", "Q3", 10.0)
        results.set_score("jane.smith@example.com", "Q4", 2.5)

        # Student 3: 15/50 points -> grade = 2.5
        results.set_score("bob.johnson@example.com", "Q1", 3.0)
        results.set_score("bob.johnson@example.com", "Q2", 4.5)
        results.set_score("bob.johnson@example.com", "Q3", 6.0)
        results.set_score("bob.johnson@example.com", "Q4", 1.5)

        return results

    def test_get_total_average(self, results_with_grades):
        """Test calculating total average grade."""
        average = results_with_grades.get_total_average()
        # Grades: 5.0, 3.5, 2.5 -> average = 3.666...
        assert average == pytest.approx(3.67, abs=0.1)

    def test_get_total_max(self, results_with_grades):
        """Test getting maximum grade."""
        max_grade = results_with_grades.get_total_max()
        # Highest score: student 1 with ~5.0
        assert max_grade == pytest.approx(5.0, abs=0.1)

    def test_get_total_min(self, results_with_grades):
        """Test getting minimum grade."""
        min_grade = results_with_grades.get_total_min()
        # Lowest score: student 3 with 2.5
        assert min_grade == pytest.approx(2.5, abs=0.1)

    def test_get_total_median(self, results_with_grades):
        """Test calculating median grade."""
        median = results_with_grades.get_total_median()
        # Grades: 2.5, 3.5, 5.0 -> median = 3.5
        assert median == pytest.approx(3.5, abs=0.1)

    def test_get_count_below_4(self, results_with_grades):
        """Test counting students with grades below 4."""
        count = results_with_grades.get_count_below_4()
        # Students with < 4: student 2 (3.5) and student 3 (2.5) = 2
        assert count == 2

    def test_get_percent_below_4(self, results_with_grades):
        """Test calculating percentage of students below 4."""
        percent = results_with_grades.get_percent_below_4()
        # 2 out of 3 students = 66.67%
        assert percent == pytest.approx(66.67, abs=0.1)

    def test_statistics_all_zeros(self, sample_class, sample_evaluation, sample_settings):
        """Test statistics when all scores are 0."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        assert results.get_total_average() == pytest.approx(1.0, abs=0.01)  # Min grade
        assert results.get_total_max() == pytest.approx(1.0, abs=0.01)
        assert results.get_total_min() == pytest.approx(1.0, abs=0.01)
        assert results.get_total_median() == pytest.approx(1.0, abs=0.01)
        assert results.get_count_below_4() == 3  # All students
        assert results.get_percent_below_4() == pytest.approx(100.0, abs=0.01)

    def test_statistics_all_perfect(self, sample_class, sample_evaluation, sample_settings):
        """Test statistics when all scores are perfect."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        # Set all students to perfect scores
        for student in sample_class.students:
            results.set_score(student.email, "Q1", 10.0)
            results.set_score(student.email, "Q2", 15.0)
            results.set_score(student.email, "Q3", 20.0)
            results.set_score(student.email, "Q4", 5.0)

        assert results.get_total_average() == pytest.approx(6.0, abs=0.01)
        assert results.get_total_max() == pytest.approx(6.0, abs=0.01)
        assert results.get_total_min() == pytest.approx(6.0, abs=0.01)
        assert results.get_total_median() == pytest.approx(6.0, abs=0.01)
        assert results.get_count_below_4() == 0
        assert results.get_percent_below_4() == pytest.approx(0.0, abs=0.01)

    def test_statistics_with_exactly_4(self, sample_class, sample_evaluation, sample_settings):
        """Test count_below_4 doesn't include exactly 4.0."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        # Student 1: exactly 4.0
        results.set_score("john.doe@example.com", "Q1", 6.0)
        results.set_score("john.doe@example.com", "Q2", 9.0)
        results.set_score("john.doe@example.com", "Q3", 12.0)
        results.set_score("john.doe@example.com", "Q4", 3.0)
        # Total: 30/50 = grade 4.0

        # Student 2: below 4.0
        results.set_score("jane.smith@example.com", "Q1", 5.0)
        results.set_score("jane.smith@example.com", "Q2", 7.5)
        results.set_score("jane.smith@example.com", "Q3", 10.0)
        results.set_score("jane.smith@example.com", "Q4", 2.5)
        # Total: 25/50 = grade 3.5

        # Student 3: above 4.0
        results.set_score("bob.johnson@example.com", "Q1", 7.0)
        results.set_score("bob.johnson@example.com", "Q2", 10.5)
        results.set_score("bob.johnson@example.com", "Q3", 14.0)
        results.set_score("bob.johnson@example.com", "Q4", 3.5)
        # Total: 35/50 = grade 4.5

        # Only student 2 should be below 4
        assert results.get_count_below_4() == 1
        assert results.get_percent_below_4() == pytest.approx(33.33, abs=0.1)

    def test_median_even_number_of_students(self, sample_evaluation, sample_settings):
        """Test median calculation with even number of students."""
        from grading import Class, Student

        # Create class with 4 students
        cls = Class("Test")
        cls.add_student(Student("A", "Student", "student.a@test.com"))
        cls.add_student(Student("B", "Student", "student.b@test.com"))
        cls.add_student(Student("C", "Student", "student.c@test.com"))
        cls.add_student(Student("D", "Student", "student.d@test.com"))

        results = Results(cls, sample_evaluation, sample_settings)

        # Grades: 1.5, 2.5, 4.0, 5.0 -> median should be (2.5+4.0)/2 = 3.25
        # Student A: grade 1.5 (5/50 points)
        results.set_score("student.a@test.com", "Q1", 1.0)
        results.set_score("student.a@test.com", "Q2", 1.5)
        results.set_score("student.a@test.com", "Q3", 2.0)
        results.set_score("student.a@test.com", "Q4", 0.5)

        # Student B: grade 2.5 (15/50 points)
        results.set_score("student.b@test.com", "Q1", 3.0)
        results.set_score("student.b@test.com", "Q2", 4.5)
        results.set_score("student.b@test.com", "Q3", 6.0)
        results.set_score("student.b@test.com", "Q4", 1.5)

        # Student C: grade 4.0 (30/50 points)
        results.set_score("student.c@test.com", "Q1", 6.0)
        results.set_score("student.c@test.com", "Q2", 9.0)
        results.set_score("student.c@test.com", "Q3", 12.0)
        results.set_score("student.c@test.com", "Q4", 3.0)

        # Student D: grade 5.0 (40/50 points)
        results.set_score("student.d@test.com", "Q1", 8.0)
        results.set_score("student.d@test.com", "Q2", 12.0)
        results.set_score("student.d@test.com", "Q3", 16.0)
        results.set_score("student.d@test.com", "Q4", 4.0)

        median = results.get_total_median()
        assert median == pytest.approx(3.25, abs=0.1)

    def test_statistics_with_dropped_questions(self, sample_class, sample_evaluation):
        """Test that statistics work correctly with dropped questions."""
        settings = GlobalSettings(dropped_questions=[4])  # Drop Q4
        results = Results(sample_class, sample_evaluation, settings)

        # Set scores for active questions only (Q1, Q2, Q3)
        # Total max now 45 instead of 50
        results.set_score("john.doe@example.com", "Q1", 10.0)
        results.set_score("john.doe@example.com", "Q2", 15.0)
        results.set_score("john.doe@example.com", "Q3", 20.0)
        # Total: 45/45 = grade 6.0

        results.set_score("jane.smith@example.com", "Q1", 5.0)
        results.set_score("jane.smith@example.com", "Q2", 7.5)
        results.set_score("jane.smith@example.com", "Q3", 10.0)
        # Total: 22.5/45 = grade 3.5

        results.set_score("bob.johnson@example.com", "Q1", 7.5)
        results.set_score("bob.johnson@example.com", "Q2", 11.25)
        results.set_score("bob.johnson@example.com", "Q3", 15.0)
        # Total: 33.75/45 = grade 4.75

        # Verify statistics
        assert results.get_total_max() == pytest.approx(6.0, abs=0.1)
        assert results.get_total_min() == pytest.approx(3.5, abs=0.1)
        assert results.get_count_below_4() == 1  # Only jane
