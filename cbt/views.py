from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Question, Option


@login_required
def cbt_test(request):
    """Display CBT test questions for selected category."""
    category = request.GET.get('category')
    
    # Only premium users can access
    if request.user.subscription_status == 'freemium':
        return redirect('student_dashboard')
    
    if not category:
        return redirect('student_dashboard')
    
    # Get questions for the category (limit to 10)
    questions = Question.objects.filter(category=category)[:10]
    
    if not questions.exists():
        return redirect('student_dashboard')
    
    # Build question data with options
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
        'time_per_question': 30,  # 30 seconds per question
    }
    
    return render(request, 'cbt/question_board.html', context)

