from .models import Course

def courses_processor(request):
    courses = Course.objects.filter(course_is_active='Yes')  # Fetch only active courses
    return {'courses': courses}