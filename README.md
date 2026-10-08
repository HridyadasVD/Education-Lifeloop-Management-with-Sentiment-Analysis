# Education Lifeloop Management with Sentiment Analysis

**Edu Friend** — a Coursera-style e-learning web app built with Django.

Students browse courses, take exams, get a personalized learning path from their results, and explore feedback sentiment in a separate analytics lab. Designed as a full education “lifeloop”: learn → assess → specialize → review feedback.

## What this project does

| Area | Description |
|------|-------------|
| **Course catalog** | Courses → subjects → chapter lessons with video, slides, notes, and discussion |
| **Exams** | MCQ assessments with PASS / FAIL results for each student |
| **Learning Path** | Recommends foundation or advanced next lessons from **exam outcomes only** |
| **Sentiment Lab** | Analyzes student feedback with **VADER** (positive / neutral / negative) — kept separate from path matching |
| **Roles** | Student, teacher, and admin flows (lesson management, exam setup, Django admin) |

## Why it fits a resume / portfolio

- End-to-end Django web application (auth, models, views, templates, media)
- Clear product logic: specialization driven by assessment results, not sentiment
- NLP add-on: VADER sentiment scoring on learner reviews
- Role-based UI for students and teachers
- Modern responsive front-end (custom CSS / light motion)

## Tech stack

- **Backend:** Python, Django 3.2
- **Database:** SQLite (local demo)
- **NLP:** vaderSentiment
- **UI:** Django templates, crispy-forms, widget-tweaks, custom CSS/JS
- **Other:** Pillow (images), role-based profiles

## Key features

- Personalized **Learning Path** after exams (FAIL → foundation lessons, PASS → advanced / standard)
- **Sentiment Lab** dashboard for feedback polarity (compound score + label)
- Lesson difficulty tags: foundation / standard / advanced
- Teacher tools for subjects, questions, and lessons
- Student discussion comments on lessons
- Demo data and sample lesson media for local walkthrough

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/

### Demo logins

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `Admin@123` |
| Student | `student` | `Student@123` |
| Teacher | `teacher` | `Teacher@123` |

Suggested flow: log in as a student → take an exam → open **Learning Path** → try **Sentiment** from the nav.

### Main pages

| Page | URL |
|------|-----|
| Home / login | `/` |
| Courses | `/cariculam/` |
| Learning Path | `/learning-path/` |
| Exams | `/student-exam` |
| Results | `/view-result` |
| Sentiment Lab | `/view_review` |
| Admin | `/admin/` |

## Project structure

```
account/     # auth, student exams, learning path, sentiment
cariculam/   # courses, subjects, lessons, comments
exam/        # exam subjects & questions (teacher)
template/    # shared base + home
static/      # theme CSS/JS
```

## Resume blurb (optional)

> Built **Edu Friend**, a Django e-learning platform with course delivery, MCQ exams, exam-based learning-path recommendations, and a VADER sentiment analysis lab for learner feedback.

---

**Repository:** https://github.com/HridyadasVD/Education-Lifeloop-Management-with-Sentiment-Analysis
