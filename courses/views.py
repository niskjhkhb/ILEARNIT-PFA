
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required # for Access Control
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404
from .models import Course
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import CustomUserCreationForm
from django.contrib.auth import logout as auth_logout


# Create views here.
def courses_processor(request):
    courses = Course.objects.filter(course_is_active='Yes')  # Fetch only active courses
    return {'courses': courses}

def home(request):
    courses = Course.objects.all()  # Fetch all courses
    context = {
        'courses': courses,
    }
    return render(request, 'courses/index.html', context)


def signup(request):        
    return render(request, 'courses/signup.html')

def index(request):
    courses = Course.objects.filter(course_is_active='Yes', course_is_featured="Yes")
    context = {
        'courses': courses,
    }
    return render(request, 'index.html', context)

def baseview(request):
    courses = Course.objects.filter(course_is_active='Yes')
    context = {
        'courses': courses,
    }
    return render(request, 'courses/baseview.html', context)

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'courses/login.html'  

def form_valid(self, form):
        # Check if "Remember Me" is selected
        remember_me = self.request.POST.get('remember', None)

        # Log in the user
        login(self.request, form.get_user())

        if not remember_me:
            # Set session to expire when the browser is closed
            self.request.session.set_expiry(0)
        else:
            # Set session to the default duration (e.g., 2 weeks)
            self.request.session.set_expiry(1209600)  # 2 weeks in seconds

        return super().form_valid(form)

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None  # Remove help text
            field.widget.attrs.update({'placeholder': field.label})  # Optional: set placeholder


from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import render, redirect

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # ✅ use your custom form here
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()  # ✅ here too
    return render(request, 'courses/signup.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'courses/profile.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_image = request.FILES.get('profile_image')

        user = request.user
        if new_username:
            user.username = new_username
            user.save()

        if new_image:
            profile = user.profile
            profile.image = new_image
            profile.save()
     
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return redirect('profile')



@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        auth_logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')  # or wherever you want after deletion
    return redirect('profile')


 
from django.shortcuts import render, get_object_or_404
from .models import Course, Progress

def course_detail(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    
    # Only check Progress if the user is authenticated
    if request.user.is_authenticated:
        progress = Progress.objects.filter(user=request.user, course=course).first()
    else:
        progress = None  # No progress for unauthenticated users

    context = {
        'course': course,
        'quiz_score': progress.quiz_score if progress else None,  # Pass the quiz score if progress exists
    }

    return render(request, 'courses/course_detail.html', context)


def topic_courses(request, topic_slug):
    topic = Topic.objects.get(topic_slug=topic_slug)
    courses = Course.objects.filter(course_is_active='Yes', course_topic=topic)
    context = {
        'courses': courses,
        'topic': topic,
    }
    return render(request, 'courses/topic_courses.html', context)


def search_courses(request):
    if request.method == "GET":
        keyword = request.GET.get('q')
        courses = Course.objects.filter(course_is_active='Yes')
        searched_courses = courses.filter(course_title__icontains=keyword) | courses.filter(course_description__icontains=keyword)
        
        context = {
            'courses': searched_courses,
            'keyword': keyword,
        }
        return render(request, 'courses/search_courses.html', context)


"""def course_detail(request, course_slug):
    try:
        course = Course.objects.get(course_slug=course_slug)
        lectures = Lecture.objects.filter(course=course.id)

        # Check
        if request.user.is_authenticated:
            enrolled = Enroll.objects.filter(course=course, user=request.user)
        else:
            enrolled = None
        

        context = {
            'course': course,
            'lectures': lectures,
            'enrolled': enrolled,
        }
        return render(request, 'courses/course_detail.html', context)

    except:
        messages.error(request, "Course Does not Exist.")
        return redirect(index)
"""
from .models import LectureProgress

@login_required  # Redirect to login if not authenticated
def lecture(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    lectures = Lecture.objects.filter(course=course)
    first_lecture = lectures.first()

    # Check if the user is enrolled
    enrolled = Enroll.objects.filter(course=course, user=request.user).exists()

    if enrolled:
        # Get the first lecture of the course

        first_lecture = lectures.first()

        # ✅ Fetch comments for the first lecture
        comments = Comment.objects.filter(lecture=first_lecture)
        completed_lectures = Lecture.objects.filter(
            lectureprogress__user=request.user,
            lectureprogress__completed=True
        )
        completed_lecture_ids = list(completed_lectures.values_list('id', flat=True))


        context = {
            'course': course,
            'lectures': lectures,
            'lecture_selected': first_lecture,
            'comments': comments,  # ✅ Pass comments to template
        }
        return render(request, 'courses/lecture.html', context)

    else:
        messages.error(request, "You must enroll in this course to access the lectures.")
        return redirect('course_detail', course_slug=course_slug)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lecture, Comment
from django.contrib.auth.decorators import login_required

@login_required
def lecture_selected(request, course_slug, lecture_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    lectures = Lecture.objects.filter(course=course)
    lecture_selected = get_object_or_404(Lecture, lecture_slug=lecture_slug, course=course)

    # Handle comment submission
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            Comment.objects.create(
                user=request.user,
                lecture=lecture_selected,
                text=comment_text
            )
            return redirect('lecture_selected', course_slug=course_slug, lecture_slug=lecture_slug)

    comments = Comment.objects.filter(lecture=lecture_selected).order_by('-id')
    completed_lectures = Lecture.objects.filter(
    lectureprogress__user=request.user,
    lectureprogress__completed=True
)
    
    completed_lecture_ids = completed_lectures.values_list('id', flat=True)

    return render(request, 'courses/lecture.html', {
        'course': course,
        'lectures': lectures,
        'lecture_selected': lecture_selected,
        'comments': comments,
        'completed_lectures': completed_lectures,
        'completed_lecture_ids': list(completed_lecture_ids),
    })








@login_required # Redirect to login if not authenticated
def enroll(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    try:
        # Check if the user is already enrolled
        if not Enroll.objects.filter(user=user, course=course).exists():
            Enroll.objects.create(user=user, course=course)
            messages.success(request, "Successfully enrolled in the course.")
        else:
            messages.info(request, "You are already enrolled in this course.")

        # Redirect to the course lectures
        return redirect('lecture', course_slug=course.course_slug)

    except Exception as e:
        messages.error(request, "Couldn't enroll in the course. Please try again later.")
        return redirect('course_detail', course_slug=course.course_slug)
      

@login_required
def enrolled_courses(request):

    try:
        courses = Enroll.objects.filter(user=request.user)
        context = {
            'courses': courses,
        }
        return render(request, 'courses/enrolled_courses.html', context)

    except:
        messages.error(request, "Couldn't Enroll to the course. Please try again later.")
        return redirect(index)
    

from django.shortcuts import render, get_object_or_404
from .models import Course
from django.shortcuts import render, get_object_or_404
from .models import Course, Quiz, Question


from django.shortcuts import render, get_object_or_404
from .models import Course, Quiz, Question, Answer

@login_required
def quiz(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    quizzes = Quiz.objects.filter(course=course, is_active='Yes')

    quiz_data = []
    for quiz in quizzes:
        questions = Question.objects.filter(quiz=quiz)
        question_data = []
        for question in questions:
            answers = Answer.objects.filter(question=question)
            # Determine if the question is multi-answer
            correct_count = answers.filter(is_correct=True).count()
            is_multi = correct_count > 1
            question_data.append({
                'question': question,
                'answers': answers,
                'is_multi': is_multi,
            })
        quiz_data.append({
            'quiz': quiz,
            'questions': question_data
        })

    context = {
        'course': course,
        'quiz_data': quiz_data,
    }
    return render(request, 'courses/quiz.html', context)



@login_required
def submit_quiz(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    quizzes = Quiz.objects.filter(course=course, is_active='Yes')

    total_questions = 0
    total_correct = 0

    for quiz in quizzes:
        for question in quiz.questions.all():
            total_questions += 1
            correct_answers = set(
                question.answers.filter(is_correct=True).values_list('id', flat=True)
            )

            # Get selected answers
            selected_ids = []

            if f'question_{question.id}' in request.POST:
                # Single answer
                selected_ids = [int(request.POST.get(f'question_{question.id}'))]
            elif f'question_{question.id}_multiple' in request.POST:
                # Multiple answers
                selected_ids = request.POST.getlist(f'question_{question.id}_multiple')
                selected_ids = [int(id) for id in selected_ids]

            # Check if selected_ids match correct ones exactly
            if set(selected_ids) == correct_answers:
                total_correct += 1

    percentage_score = (total_correct / total_questions) * 100 if total_questions > 0 else 0

    # Save progress
    progress, created = Progress.objects.get_or_create(user=request.user, course=course)
    progress.quiz_score = percentage_score
    progress.save()

    messages.success(request, f"You scored {percentage_score:.2f}%!")
    return redirect('course_detail', course_slug=course.course_slug)


from .models import Progress, Course

@login_required
def progress_dashboard(request):
    user = request.user
    # Get all enrolled courses
    enrolled_courses = Enroll.objects.filter(user=user).select_related('course')
    
    course_progress_list = []
    
    for enrollment in enrolled_courses:
        course = enrollment.course
        total_lectures = course.lectures.count()
        
        # Get completed lectures for this course
        completed_lectures = LectureProgress.objects.filter(
            user=user,
            lecture__course=course,
            completed=True
        ).count()
        
        # Calculate lecture completion percentage
        lecture_completion = (completed_lectures / total_lectures) * 100 if total_lectures > 0 else 0
        
        # Get quiz progress if exists
        try:
            progress = Progress.objects.get(user=user, course=course)
            quiz_score = progress.quiz_score or 0
        except Progress.DoesNotExist:
            quiz_score = 0
        
        # Calculate overall progress (50% lectures, 50% quiz)
        overall_progress = (lecture_completion + quiz_score) / 2 if quiz_score > 0 else lecture_completion
        
        course_progress_list.append({
            'course': course,
            'lecture_completion': lecture_completion,
            'quiz_score': quiz_score,
            'overall_progress': overall_progress,
            'remaining_progress': 100 - overall_progress,
        })
    
    context = {
        'course_progress_list': course_progress_list,
    }

    return render(request, 'courses/progress_dashboard.html', context)



from django.shortcuts import get_object_or_404, redirect
from .models import Course, Lecture, Comment

@login_required
def add_comment(request, course_slug, lecture_slug):
    # Fetch the course and lecture based on the slugs
    course = get_object_or_404(Course, course_slug=course_slug)
    lecture = get_object_or_404(Lecture, lecture_slug=lecture_slug)

    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            # Create and save the comment
            Comment.objects.create(
                user=request.user,
                text=comment_text,
                lecture=lecture
            )
        return redirect('lecture_selected', course_slug=course_slug, lecture_slug=lecture_slug)


@login_required
def delete_comment(request, comment_id):
    # Get the comment to delete
    comment = get_object_or_404(Comment, id=comment_id)

    # Ensure that the user is the one who created the comment
    if comment.user == request.user:
        comment.delete()
        messages.success(request, "Your comment has been deleted.")
    else:
        messages.error(request, "You can only delete your own comments.")

    # Redirect back to the lecture page
    return redirect('lecture_selected', course_slug=comment.lecture.course.course_slug, lecture_slug=comment.lecture.lecture_slug)

from .models import Lecture, Course, LectureProgress
from django.http import JsonResponse


from django.shortcuts import redirect

@login_required
def mark_lecture_complete(request, course_slug, lecture_slug):
    if request.method == 'POST':
        lecture = get_object_or_404(Lecture, lecture_slug=lecture_slug)
        # Create or update lecture progress
        LectureProgress.objects.update_or_create(
            user=request.user,
            lecture=lecture,
            defaults={'completed': True}
        )
        # Ensure the user is enrolled in the course
        course = get_object_or_404(Course, course_slug=course_slug)
        Enroll.objects.get_or_create(user=request.user, course=course)
        
        return redirect('lecture_selected', course_slug=course_slug, lecture_slug=lecture_slug)
    return redirect('lecture_selected', course_slug=course_slug, lecture_slug=lecture_slug)


def enroll_user_in_course(user, course):
    Enroll.objects.get_or_create(user=user, course=course)
    for lecture in course.lectures.all():
        LectureProgress.objects.get_or_create(user=user, lecture=lecture)
