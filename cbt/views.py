from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Option


@login_required
def cbt_test(request):
    """Display CBT test questions for selected category or mock exam."""
    category = request.GET.get('category')
    mode = request.GET.get('mode', 'category')

    if request.user.subscription_status == 'freemium':
        return redirect('subscription_page')

    if mode == 'mock':
        daily_limit = {
            'basic': 50,
            'standard': 100,
            'pro': 150,
        }.get(request.user.subscription_plan, 0)

        if daily_limit <= 0:
            return redirect('subscription_page')

        questions = list(Question.objects.all().order_by('?')[:daily_limit])
        question_data = []
        for q in questions:
            option = q.option
            question_data.append({
                'id': q.id,
                'text': q.text,
                'options': {
                    'a': option.option_a,
                    'b': option.option_b,
                    'c': option.option_c,
                    'd': option.option_d,
                },
                'correct_answer': option.correct_option,
                'rationale': option.rationale,
            })

        context = {
            'category': 'mock_exam',
            'category_display': 'Mock Exam',
            'questions': question_data,
            'total_questions': len(question_data),
            'time_per_question': 30,
            'daily_limit': daily_limit,
            'subscription_plan': request.user.get_subscription_plan_display() if request.user.subscription_plan else 'Not selected',
        }
        return render(request, 'cbt/question_board.html', context)

    if not category:
        return redirect('student_dashboard')

    questions = Question.objects.filter(category=category).order_by('?')[:10]

    if not questions.exists():
        return redirect('student_dashboard')

    question_data = []
    for q in questions:
        option = q.option
        question_data.append({
            'id': q.id,
            'text': q.text,
            'options': {
                'a': option.option_a,
                'b': option.option_b,
                'c': option.option_c,
                'd': option.option_d,
            },
            'correct_answer': option.correct_option,
            'rationale': option.rationale,
        })

    context = {
        'category': category,
        'category_display': dict(Question.Category.choices).get(category, category),
        'questions': question_data,
        'total_questions': len(question_data),
        'time_per_question': 30,
    }

    return render(request, 'cbt/question_board.html', context)

