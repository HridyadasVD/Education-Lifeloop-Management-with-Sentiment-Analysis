from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from exam import models as QMODEL
from .forms import Userform, UserProfileInfoform
from .models import Contact, StudentReview, User_Profile
from .path_service import build_learning_path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def _polarity_from_compound(compound):
    if compound >= 0.05:
        return StudentReview.POSITIVE
    if compound <= -0.05:
        return StudentReview.NEGATIVE
    return StudentReview.NEUTRAL


def index(request):
    return render(request, 'home.html')


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = Userform(data=request.POST)
        profile_form = UserProfileInfoform(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = Userform()
        profile_form = UserProfileInfoform()

    return render(
        request,
        'register.html',
        {
            'registered': registered,
            'user_form': user_form,
            'profile_form': profile_form,
        },
    )


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                messages.success(
                    request,
                    f'Welcome back, {user.username}. Open Exams to test yourself, then check Learning Path.',
                )
                return HttpResponseRedirect(reverse('index'))
            return render(request, 'home.html', {'login_error': 'Account is deactivated'})
        return render(
            request,
            'home.html',
            {'login_error': 'Please check username and password'},
        )
    return HttpResponseRedirect(reverse('index'))


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def learning_path(request):
    profile, _ = User_Profile.objects.get_or_create(
        user=request.user,
        defaults={'user_type': User_Profile.student},
    )
    path_data = build_learning_path(profile)
    return render(request, 'learning_path.html', {'path': path_data})


@login_required
def student_exam_view(request):
    courses = []
    for exam in QMODEL.ExamSubject.objects.select_related('subject_name').all():
        question_count = QMODEL.Question.objects.filter(course=exam).count()
        courses.append({
            'exam': exam,
            'question_count': question_count,
            'ready': question_count > 0,
        })
    return render(request, 'student_exam.html', {'courses': courses})


@login_required
def take_exam_view(request, pk):
    course = get_object_or_404(QMODEL.ExamSubject, id=pk)
    questions = QMODEL.Question.objects.filter(course=course)
    total_marks = sum(q.marks for q in questions)
    if questions.count() == 0:
        messages.warning(request, 'This exam has no questions yet. Pick another subject.')
        return HttpResponseRedirect(reverse('student-exam'))
    return render(
        request,
        'take_exam.html',
        {
            'course': course,
            'total_questions': questions.count(),
            'total_marks': total_marks,
        },
    )


@login_required
def start_exam_view(request, pk):
    course = get_object_or_404(QMODEL.ExamSubject, id=pk)
    questions = QMODEL.Question.objects.filter(course=course)
    response = render(
        request,
        'start_exam.html',
        {'course': course, 'questions': questions},
    )
    response.set_cookie('course_id', course.id)
    return response


@login_required
def calculate_marks_view(request):
    course_id = request.COOKIES.get('course_id')
    if course_id is None:
        return HttpResponseRedirect(reverse('student-exam'))

    course = get_object_or_404(QMODEL.ExamSubject, id=course_id)
    questions = list(QMODEL.Question.objects.filter(course=course))
    total_marks = 0
    for index, question in enumerate(questions):
        selected_ans = request.COOKIES.get(str(index + 1))
        if selected_ans == question.answer:
            total_marks += question.marks

    student, _ = User_Profile.objects.get_or_create(
        user=request.user,
        defaults={'user_type': User_Profile.student},
    )
    status = 'FAIL' if total_marks < (course.total_marks / 2) else 'PASS'
    result = QMODEL.Result(
        marks=total_marks,
        exam=course,
        student=student,
        status=status,
    )
    result.save()
    if status == 'PASS':
        messages.success(
            request,
            f'Exam submitted: {total_marks}/{course.total_marks} — PASS. '
            'Your Learning Path now suggests advanced or next-level classes.',
        )
    else:
        messages.warning(
            request,
            f'Exam submitted: {total_marks}/{course.total_marks} — FAIL. '
            'Your Learning Path now suggests foundation classes for this subject.',
        )
    messages.info(
        request,
        'Tip: use Sentiment Lab anytime to analyze feedback — it is separate from class recommendations.',
    )
    return HttpResponseRedirect(reverse('learning-path'))


@login_required
def view_result_view(request):
    courses = QMODEL.ExamSubject.objects.select_related('subject_name').all()
    return render(request, 'view_result.html', {'courses': courses})


@login_required
def check_marks_view(request, pk):
    course = get_object_or_404(QMODEL.ExamSubject, id=pk)
    student, _ = User_Profile.objects.get_or_create(
        user=request.user,
        defaults={'user_type': User_Profile.student},
    )
    results = QMODEL.Result.objects.filter(exam=course, student=student).order_by('-date')
    return render(request, 'check_marks.html', {'results': results, 'course': course})


@login_required
def student_marks_view(request):
    courses = QMODEL.ExamSubject.objects.select_related('subject_name').all()
    return render(request, 'student_marks.html', {'courses': courses})


@login_required
def all_mark(request):
    results = QMODEL.Result.objects.select_related('student', 'exam', 'exam__subject_name').all()
    return render(request, 'view_student_mark.html', {'results': results})


def contact(request):
    if request.method == 'POST':
        Contact.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            content=request.POST.get('content'),
        )
        return render(request, 'home.html', {'msg': 'Details Successfully Saved.'})
    return render(request, 'home.html', {})


@login_required
def review(request):
    msg = None
    if request.method == 'POST':
        review_text = request.POST.get('review', '').strip()
        student_name = request.POST.get('student') or request.user.username
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(review_text)
        compound = scores.get('compound', 0.0)
        if not review_text:
            messages.error(request, 'Please enter feedback text to analyze.')
            return render(
                request,
                'review.html',
                {'default_student': request.user.username},
            )
        polarity = _polarity_from_compound(compound)
        StudentReview.objects.create(
            student=student_name,
            review=review_text,
            value=str(scores),
            compound=compound,
            polarity=polarity,
        )
        messages.success(
            request,
            f'Sentiment saved as {polarity.title()} (compound {compound:.3f}).',
        )
        return HttpResponseRedirect(reverse('view_review'))
    return render(request, 'review.html', {'msg': msg, 'default_student': request.user.username})


@login_required
def view_review(request):
    reviews = StudentReview.objects.all().order_by('-id')
    mine = [item for item in reviews if item.student == request.user.username]
    return render(
        request,
        'view_review.html',
        {
            'review': reviews,
            'my_reviews': mine,
            'show_mine': bool(mine),
        },
    )
