
from django.db import models
from django.contrib.auth.models import User



# Custome Choices Here
IS_ACTIVE = (
    ('Yes', 'Yes'),
    ('No', 'No')
)

class Topic(models.Model):
    topic_title = models.CharField(max_length=50, verbose_name="Topic Title")
    topic_slug = models.SlugField(max_length=55, verbose_name="Topic Slug")
    topic_description = models.TextField(blank=True, null=True, verbose_name="Topic Description")
    # topic_parent = models.ForeignKey(Topic, verbose_name="Parent Topic", on_delete=models.DO_NOTHING)
    topic_image = models.ImageField(upload_to="topics/", blank=True, null=True)

    topic_is_active = models.CharField(
        choices = IS_ACTIVE,
        default='Yes',
        max_length = 10,
        verbose_name = "Is Active?"
    )
    topic_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    topic_updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    # Meta for SEO
    meta_topic_title = models.CharField(max_length=60, blank=True, null=True, verbose_name="SEO Topic Title (60 Characters Long)")
    meta_topic_keywords = models.TextField(blank=True, null=True, verbose_name="SEO Topic Keywords, Separated by Commas")
    meta_topic_description = models.TextField(blank=True, null=True, verbose_name="SEO Topic Description (160 characters long)")
    
    def __str__(self):
        return self.topic_title
    

class Course(models.Model):
    course_title = models.CharField(max_length=200, verbose_name="Course Title")
    course_slug = models.SlugField(verbose_name="Course Slug")
    course_description = models.TextField(blank=True, null=True, verbose_name="Course Description")
    course_topic = models.ManyToManyField(Topic, verbose_name="Course Topic")
    course_image = models.ImageField(upload_to="courses/", blank=True, null=True)
    course_is_active = models.CharField(
        choices = IS_ACTIVE,
        default = 'Yes',
        max_length=50,
        verbose_name="Is Active?"
        )
    course_is_featured = models.CharField(
        choices = IS_ACTIVE,
        default = 'Yes',
        max_length=50,
        verbose_name="Is Featured?"
        )
    course_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    course_updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    # Meta for SEO
    seo_course_title = models.CharField(max_length=60, blank=True, null=True, verbose_name="SEO Course Title (60 Characters Long)")
    seo_course_keywords = models.TextField(blank=True, null=True, verbose_name="SEO for Course Keywords, Separated by Commas")
    seo_course_description = models.TextField(blank=True, null=True, verbose_name="SEO Course Description (160 Characters Long)")
    
    class Meta:
        ordering = ('-course_created_at', )
        
    def __str__(self):
        return self.course_title


class Lecture(models.Model):
    lecture_title = models.CharField(max_length=255, verbose_name="Lecture Title")
    lecture_slug = models.SlugField(verbose_name="Lecture Slug")
    lecture_description = models.TextField(blank=True, null=True, verbose_name="Lecture Description")
    course = models.ForeignKey(Course, verbose_name="Course", on_delete=models.CASCADE, related_name='lectures')
    lecture_file = models.FileField(upload_to="files/", blank=True, null=True)
    lecture_video = models.CharField(max_length=150, blank=True, null=True, verbose_name="Video ID")

    lecture_previewable = models.CharField(
        choices = IS_ACTIVE,
        default = 'Yes',
        max_length=50,
        verbose_name="Is Previewable?"
        )
    lecture_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    lecture_updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    # Meta SEO
    seo_lecture_title = models.CharField(max_length=60, blank=True, null=True, verbose_name="SEO Lecture Title (60 Characters Long)")
    seo_lecture_keyword = models.TextField(blank=True, null=True, verbose_name="SEO Lecture Keywords, Separated by Comma")
    seo_lecture_description = models.TextField(blank=True, null=True, verbose_name="SEO Lecture Description (160 Characters Long)")

    def __str__(self):
        return self.lecture_title


class Enroll(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name="Course", on_delete=models.CASCADE)
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name="Enrolled Date")

    def __str__(self):
        return self.course.course_title
    
    # Quiz model (related to a specific course)
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    is_active = models.CharField(choices=IS_ACTIVE, default='Yes', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.course_title}"

# Question model (belongs to a Quiz)
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question: {self.text[:50]}"

#  Answer model (belongs to a Question)
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer: {self.text} (Correct: {self.is_correct})"

#Progress model (to track user course completion)
class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_lectures = models.ManyToManyField(Lecture, blank=True)
    quiz_score = models.FloatField(default=0.0)  
    completed_quizzes = models.ManyToManyField(Quiz, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s progress in {self.course.course_title}"

from django.db import models
from django.contrib.auth.models import User
from courses.models import Lecture

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()  # This is where the comment text is stored
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.lecture.lecture_title}'


# Review model (for Courses)
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=1)  # from 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')  # one review per user per course

    def __str__(self):
        return f"{self.user.username}'s review of {self.course.course_title}"
    

    
    
class LectureProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'lecture')




