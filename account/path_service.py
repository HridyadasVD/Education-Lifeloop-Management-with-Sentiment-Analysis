from exam import models as exam_models
from cariculam.models import Lesson, Subject


def _lesson_payload(lesson):
    return {
        'id': lesson.id,
        'name': lesson.name,
        'position': lesson.position,
        'difficulty': lesson.difficulty,
        'difficulty_label': lesson.get_difficulty_display(),
        'url_kwargs': {
            'course': lesson.course.slug,
            'subject': lesson.subject.slug,
            'slug': lesson.slug,
        },
    }


def _lessons_for_subject(subject, difficulty=None, limit=4):
    qs = Lesson.objects.filter(subject=subject).order_by('position')
    if difficulty:
        matched = list(qs.filter(difficulty=difficulty)[:limit])
        if matched:
            return [_lesson_payload(lesson) for lesson in matched]
    return [_lesson_payload(lesson) for lesson in qs[:limit]]


def _latest_results_by_exam(profile):
    latest = {}
    results = (
        exam_models.Result.objects
        .filter(student=profile)
        .select_related('exam', 'exam__subject_name', 'exam__subject_name__course')
        .order_by('-date', '-id')
    )
    for result in results:
        if result.exam_id not in latest:
            latest[result.exam_id] = result
    return list(latest.values())


def build_learning_path(profile):
    """
    Build personalized lesson recommendations from exam PASS/FAIL results.
    Sentiment analysis is intentionally not used here.
    """
    latest_results = _latest_results_by_exam(profile)
    path_items = []

    for result in latest_results:
        subject = result.exam.subject_name
        status = (result.status or '').upper()
        if status == 'FAIL':
            recommendations = _lessons_for_subject(subject, difficulty=Lesson.FOUNDATION)
            guidance = 'Focus on foundation classes to rebuild this subject.'
        else:
            recommendations = _lessons_for_subject(subject, difficulty=Lesson.ADVANCED)
            if not recommendations or all(
                item['difficulty'] != Lesson.ADVANCED for item in recommendations
            ):
                recommendations = _lessons_for_subject(subject, difficulty=Lesson.STANDARD)
            guidance = 'You passed — move into advanced or next-level chapters.'

        path_items.append({
            'exam': result.exam,
            'subject': subject,
            'course': subject.course,
            'marks': result.marks,
            'status': status,
            'date': result.date,
            'guidance': guidance,
            'recommendations': recommendations,
        })

    starter_exams = []
    starter_lessons = []
    if not path_items:
        starter_exams = list(exam_models.ExamSubject.objects.select_related('subject_name')[:6])
        for subject in Subject.objects.all()[:4]:
            starter_lessons.extend(_lessons_for_subject(subject, limit=2))

    return {
        'items': path_items,
        'has_results': bool(path_items),
        'starter_exams': starter_exams,
        'starter_lessons': starter_lessons,
    }
