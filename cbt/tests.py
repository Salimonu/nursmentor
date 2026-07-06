from django.test import TestCase

from .models import Question, Option


class QuestionModelTests(TestCase):
    def test_create_question_with_category(self):
        question = Question.objects.create(
            text='What is the primary goal of nursing care?',
            category=Question.Category.FUNDAMENTALS_OF_NURSING,
        )
        option = Option.objects.create(
            question=question,
            option_a='Provide comfort',
            option_b='Promote health and prevent illness',
            option_c='Administer medications',
            option_d='Perform surgeries',
            correct_option='b',
            rationale='The primary goal of nursing is to promote health and prevent illness.',
        )

        self.assertEqual(question.category, Question.Category.FUNDAMENTALS_OF_NURSING)
        self.assertEqual(question.get_category_display(), 'Fundamentals of Nursing')
        self.assertEqual(option.question, question)
        self.assertEqual(option.correct_option, 'b')
        self.assertIn('promote health', option.rationale)

