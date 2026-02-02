"""
Unit tests for Results class core functionality.

Tests Results initialization, score management, and the critical
Swiss grading formula calculation.
"""
import pytest
from grading import Results, GlobalSettings, Question


@pytest.mark.unit
class TestResultsInitialization:
    """Tests for Results class initialization."""

    def test_basic_initialization(self, sample_class, sample_evaluation, sample_settings):
        """Test basic Results initialization."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        assert results.class_ == sample_class
        assert results.evaluation == sample_evaluation
        assert results.settings == sample_settings
        assert len(results.scores) == 3  # 3 students

    def test_scores_initialized_with_active_questions(self, sample_class, sample_evaluation, sample_settings):
        """Test that scores are initialized only for active questions."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        # All 4 questions should be active (no dropped questions)
        for student in sample_class.students:
            assert len(results.scores[student.email]) == 4
            assert 'Q1' in results.scores[student.email]
            assert 'Q2' in results.scores[student.email]
            assert 'Q3' in results.scores[student.email]
            assert 'Q4' in results.scores[student.email]

    def test_initialization_with_dropped_questions(self, sample_class, sample_evaluation):
        """Test initialization with dropped questions."""
        settings = GlobalSettings(dropped_questions=[2])  # Drop Q2
        results = Results(sample_class, sample_evaluation, settings)

        # Only 3 questions should be active (Q1, Q3, Q4)
        for student in sample_class.students:
            assert len(results.scores[student.email]) == 3
            assert 'Q1' in results.scores[student.email]
            assert 'Q2' not in results.scores[student.email]  # Dropped
            assert 'Q3' in results.scores[student.email]
            assert 'Q4' in results.scores[student.email]

    def test_initialization_with_given_questions(self, sample_class, sample_evaluation):
        """Test initialization with given questions (full points automatically)."""
        settings = GlobalSettings(given_questions=[1])  # Give Q1
        results = Results(sample_class, sample_evaluation, settings)

        # Q1 should have full points for all students
        q1_points = sample_evaluation.questions[0].points  # 10.0
        for student in sample_class.students:
            assert results.scores[student.email]['Q1'] == q1_points
            # Other questions should be 0
            assert results.scores[student.email]['Q2'] == 0.0
            assert results.scores[student.email]['Q3'] == 0.0
            assert results.scores[student.email]['Q4'] == 0.0

    def test_initialization_with_both_dropped_and_given(self, sample_class, sample_evaluation):
        """Test initialization with both dropped and given questions."""
        settings = GlobalSettings(
            dropped_questions=[3],  # Drop Q3
            given_questions=[1]     # Give Q1
        )
        results = Results(sample_class, sample_evaluation, settings)

        # Q3 should not be in scores (dropped)
        # Q1 should have full points (given)
        q1_points = sample_evaluation.questions[0].points
        for student in sample_class.students:
            assert len(results.scores[student.email]) == 3  # Q1, Q2, Q4 only
            assert 'Q3' not in results.scores[student.email]
            assert results.scores[student.email]['Q1'] == q1_points

    def test_scores_initialized_to_zero(self, sample_class, sample_evaluation, sample_settings):
        """Test that all scores are initialized to 0.0."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        for student in sample_class.students:
            for question_uid in results.scores[student.email]:
                # Except for given questions, all should be 0
                assert results.scores[student.email][question_uid] == 0.0


@pytest.mark.unit
class TestResultsScoreManagement:
    """Tests for get_score and set_score methods."""

    def test_get_score_valid(self, sample_results):
        """Test getting a score for valid student and question."""
        # Initially 0.0
        score = sample_results.get_score("john.doe@example.com", 0)  # Q1
        assert score == 0.0

    def test_set_and_get_score(self, sample_results):
        """Test setting and getting a score."""
        student_email = "john.doe@example.com"
        question_uid = "Q1"

        sample_results.set_score(student_email, question_uid, 7.5)
        retrieved_score = sample_results.get_score(student_email, 0)  # Q1 is index 0

        assert retrieved_score == 7.5

    def test_set_score_invalid_student_raises_error(self, sample_results):
        """Test that setting score for invalid student raises error."""
        with pytest.raises(ValueError, match="Invalid student email"):
            sample_results.set_score("nonexistent@test.com", "Q1", 5.0)

    def test_set_score_invalid_question_uid_raises_error(self, sample_results):
        """Test that setting score for invalid question UID raises error."""
        with pytest.raises(ValueError):
            sample_results.set_score("john.doe@example.com", "Q99", 5.0)

    def test_get_score_invalid_student_raises_error(self, sample_results):
        """Test that getting score for invalid student raises error."""
        with pytest.raises(ValueError, match="Invalid student email"):
            sample_results.get_score("nonexistent@test.com", 0)

    def test_get_score_dropped_question_raises_error(self, sample_class, sample_evaluation):
        """Test that getting score for dropped question raises error."""
        settings = GlobalSettings(dropped_questions=[2])  # Drop Q2
        results = Results(sample_class, sample_evaluation, settings)

        with pytest.raises(ValueError, match="dropped"):
            results.get_score("john.doe@example.com", 1)  # Q2 is index 1

    def test_set_score_dropped_question_raises_error(self, sample_class, sample_evaluation):
        """Test that setting score for dropped question raises error."""
        settings = GlobalSettings(dropped_questions=[2])  # Drop Q2
        results = Results(sample_class, sample_evaluation, settings)

        with pytest.raises(ValueError):
            results.set_score("john.doe@example.com", "Q2", 5.0)


@pytest.mark.unit
class TestCalculateStudentScore:
    """Tests for the calculate_student_score method and Swiss grading formula."""

    def test_calculate_score_all_zeros(self, sample_results):
        """Test calculating score when all question scores are 0."""
        grade = sample_results.calculate_student_score("john.doe@example.com")
        # Formula: ((0 / 50) * 5) + 1 = 1.0
        assert grade == pytest.approx(1.0, abs=0.01)

    def test_calculate_score_perfect(self, sample_results):
        """Test calculating score with perfect scores."""
        student_email = "john.doe@example.com"
        # Set all questions to max points
        sample_results.set_score(student_email, "Q1", 10.0)
        sample_results.set_score(student_email, "Q2", 15.0)
        sample_results.set_score(student_email, "Q3", 20.0)
        sample_results.set_score(student_email, "Q4", 5.0)
        # Total: 50 points out of 50
        # Formula: ((50 / 50) * 5) + 1 = 6.0

        grade = sample_results.calculate_student_score(student_email)
        assert grade == pytest.approx(6.0, abs=0.01)

    def test_calculate_score_half_points(self, sample_results):
        """Test calculating score with half points."""
        student_email = "john.doe@example.com"
        # Set all questions to half points
        sample_results.set_score(student_email, "Q1", 5.0)
        sample_results.set_score(student_email, "Q2", 7.5)
        sample_results.set_score(student_email, "Q3", 10.0)
        sample_results.set_score(student_email, "Q4", 2.5)
        # Total: 25 points out of 50
        # Formula: ((25 / 50) * 5) + 1 = 3.5

        grade = sample_results.calculate_student_score(student_email)
        assert grade == pytest.approx(3.5, abs=0.01)

    def test_calculate_score_with_coefficient(self, sample_class, sample_settings):
        """Test score calculation with weighted questions."""
        from grading import Evaluation
        # Create evaluation with different coefficients
        questions = [
            Question("Part 1", "Q1", 10.0, 1.0),
            Question("Part 1", "Q2", 10.0, 2.0),  # Double weight
        ]
        evaluation = Evaluation("Test", questions)
        results = Results(sample_class, evaluation, sample_settings)

        student_email = "john.doe@example.com"
        results.set_score(student_email, "Q1", 10.0)  # 10 * 1.0 = 10
        results.set_score(student_email, "Q2", 10.0)  # 10 * 2.0 = 20
        # Total: 30 out of 30
        # Formula: ((30 / 30) * 5) + 1 = 6.0

        grade = results.calculate_student_score(student_email)
        assert grade == pytest.approx(6.0, abs=0.01)

    def test_calculate_score_with_bonus_points(self, sample_class, sample_evaluation):
        """Test score calculation with bonus points."""
        settings = GlobalSettings(bonus_points=5.0)
        results = Results(sample_class, sample_evaluation, settings)

        student_email = "john.doe@example.com"
        # Set to 45 points out of 50
        results.set_score(student_email, "Q1", 10.0)
        results.set_score(student_email, "Q2", 15.0)
        results.set_score(student_email, "Q3", 15.0)
        results.set_score(student_email, "Q4", 5.0)
        # Total: 45 points
        # Formula: ((45 / (50 - 5)) * 5) + 1 = ((45 / 45) * 5) + 1 = 6.0

        grade = results.calculate_student_score(student_email)
        assert grade == pytest.approx(6.0, abs=0.01)

    def test_calculate_score_with_added_points(self, sample_class, sample_evaluation):
        """Test score calculation with added points."""
        settings = GlobalSettings(added_points=5.0)
        results = Results(sample_class, sample_evaluation, settings)

        student_email = "john.doe@example.com"
        # Set to 20 points out of 50
        results.set_score(student_email, "Q1", 5.0)
        results.set_score(student_email, "Q2", 7.5)
        results.set_score(student_email, "Q3", 5.0)
        results.set_score(student_email, "Q4", 2.5)
        # Total: 20 + 5 (added) = 25 points
        # Formula: ((25 / 50) * 5) + 1 = 3.5

        grade = results.calculate_student_score(student_email)
        assert grade == pytest.approx(3.5, abs=0.01)

    def test_calculate_score_with_dropped_questions(self, sample_class, sample_evaluation):
        """Test score calculation excludes dropped questions."""
        settings = GlobalSettings(dropped_questions=[4])  # Drop Q4 (5 points)
        results = Results(sample_class, sample_evaluation, settings)

        student_email = "john.doe@example.com"
        # Set all active questions to max points
        results.set_score(student_email, "Q1", 10.0)
        results.set_score(student_email, "Q2", 15.0)
        results.set_score(student_email, "Q3", 20.0)
        # Q4 is dropped, total max is now 45 instead of 50
        # Total: 45 out of 45
        # Formula: ((45 / 45) * 5) + 1 = 6.0

        grade = results.calculate_student_score(student_email)
        assert grade == pytest.approx(6.0, abs=0.01)

    def test_calculate_score_with_given_questions(self, sample_class, sample_evaluation):
        """Test score calculation with given questions."""
        settings = GlobalSettings(given_questions=[1])  # Give Q1 (10 points)
        results = Results(sample_class, sample_evaluation, settings)

        student_email = "john.doe@example.com"
        # Q1 is already 10.0 (given), set others to 0
        # Total: 10 out of 50
        # Formula: ((10 / 50) * 5) + 1 = 2.0

        grade = results.calculate_student_score(student_email)
        assert grade == pytest.approx(2.0, abs=0.01)

    def test_calculate_score_clamped_at_six(self, sample_class, sample_evaluation):
        """Test that grades are clamped to max 6.0."""
        settings = GlobalSettings(added_points=50.0)  # Large added points
        results = Results(sample_class, sample_evaluation, settings)

        student_email = "john.doe@example.com"
        results.set_score(student_email, "Q1", 10.0)
        results.set_score(student_email, "Q2", 15.0)
        results.set_score(student_email, "Q3", 20.0)
        results.set_score(student_email, "Q4", 5.0)
        # Total: 50 + 50 = 100, would give > 6.0 without clamping

        grade = results.calculate_student_score(student_email, clamp=True)
        assert grade == pytest.approx(6.0, abs=0.01)

    def test_calculate_score_no_clamp(self, sample_class, sample_evaluation):
        """Test calculate_student_score without clamping."""
        settings = GlobalSettings(added_points=50.0)
        results = Results(sample_class, sample_evaluation, settings)

        student_email = "john.doe@example.com"
        results.set_score(student_email, "Q1", 10.0)
        results.set_score(student_email, "Q2", 15.0)
        results.set_score(student_email, "Q3", 20.0)
        results.set_score(student_email, "Q4", 5.0)
        # Total: 100 out of 50
        # Formula: ((100 / 50) * 5) + 1 = 11.0

        grade = results.calculate_student_score(student_email, clamp=False)
        assert grade == pytest.approx(11.0, abs=0.01)

    def test_calculate_score_round_up_behavior(self, sample_class, sample_evaluation, sample_settings):
        """Test that score calculation uses round_up correctly."""
        results = Results(sample_class, sample_evaluation, sample_settings)

        student_email = "john.doe@example.com"
        # Set scores to get a grade that needs rounding
        results.set_score(student_email, "Q1", 5.5)
        results.set_score(student_email, "Q2", 8.0)
        results.set_score(student_email, "Q3", 10.5)
        results.set_score(student_email, "Q4", 2.5)
        # Total: 26.5 out of 50
        # Formula: ((26.5 / 50) * 5) + 1 = 3.65
        # round_up(3.65, 1) = 3.7

        grade = results.calculate_student_score(student_email)
        assert grade == pytest.approx(3.7, abs=0.01)

    def test_calculate_score_complex_scenario(self, sample_class, sample_evaluation):
        """Test score calculation with all settings combined."""
        settings = GlobalSettings(
            bonus_points=5.0,
            added_points=2.0,
            dropped_questions=[4],  # Drop Q4 (5 points)
            given_questions=[1]     # Give Q1 (10 points)
        )
        results = Results(sample_class, sample_evaluation, settings)

        student_email = "john.doe@example.com"
        # Q1 is given: 10.0
        # Set Q2 and Q3
        results.set_score(student_email, "Q2", 10.0)
        results.set_score(student_email, "Q3", 15.0)
        # Q4 is dropped
        # Total: 10 + 10 + 15 + 2 (added) = 37
        # Max score: 10 + 15 + 20 = 45 (Q4 dropped)
        # Formula: ((37 / (45 - 5)) * 5) + 1 = ((37 / 40) * 5) + 1 = 5.625
        # round_up(5.625, 1) = 5.7

        grade = results.calculate_student_score(student_email)
        assert grade == pytest.approx(5.7, abs=0.01)


@pytest.mark.unit
class TestResultsHelperMethods:
    """Tests for Results helper methods."""

    def test_active_question_indices_no_dropped(self, sample_results):
        """Test active_question_indices with no dropped questions."""
        indices = sample_results.active_question_indices()
        assert indices == [0, 1, 2, 3]  # All 4 questions active

    def test_active_question_indices_with_dropped(self, sample_class, sample_evaluation):
        """Test active_question_indices with dropped questions."""
        settings = GlobalSettings(dropped_questions=[2, 4])  # Drop Q2 and Q4
        results = Results(sample_class, sample_evaluation, settings)

        indices = results.active_question_indices()
        assert indices == [0, 2]  # Q1 and Q3 only

    def test_active_question_uids_no_dropped(self, sample_results):
        """Test active_question_uids with no dropped questions."""
        uids = sample_results.active_question_uids()
        assert uids == ['Q1', 'Q2', 'Q3', 'Q4']

    def test_active_question_uids_with_dropped(self, sample_class, sample_evaluation):
        """Test active_question_uids with dropped questions."""
        settings = GlobalSettings(dropped_questions=[3])  # Drop Q3
        results = Results(sample_class, sample_evaluation, settings)

        uids = results.active_question_uids()
        assert uids == ['Q1', 'Q2', 'Q4']  # Q3 dropped

    def test_get_question_by_index(self, sample_results):
        """Test get_question_by_index method."""
        q1 = sample_results.get_question_by_index(0)
        assert q1.title == "Question 1"
        assert q1.points == 10.0

        q3 = sample_results.get_question_by_index(2)
        assert q3.title == "Question 3"
        assert q3.points == 20.0
