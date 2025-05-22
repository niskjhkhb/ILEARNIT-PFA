from django.contrib import admin
from .models import Topic, Course, Lecture, Enroll
from .models import Quiz, Question, Answer, Progress, Comment, Review
from ckeditor.widgets import CKEditorWidget

from courses import models

class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic_title', 'topic_slug', 'topic_is_active')
    list_editable = ('topic_slug', 'topic_is_active')
    list_filter = ('topic_is_active', 'topic_created_at')
    list_per_page = 10
    search_fields = ('topic_title', 'topic_description')
    prepopulated_fields = {"topic_slug": ("topic_title", )}


class CourseAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.RichTextField: {'widget': CKEditorWidget}
    }
    list_display = ('course_title', 'course_slug', 'course_is_active')
    list_editable = ('course_slug', 'course_is_active')
    list_filter = ('course_is_active', 'course_created_at')
    list_per_page = 10
    search_fields = ('course_title', 'course_description')
    prepopulated_fields = {"course_slug": ("course_title", )}


class LectureAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.RichTextField: {'widget': CKEditorWidget}
    }
    list_display = ('lecture_title', 'course', 'lecture_slug', 'lecture_previewable')
    list_editable = ('lecture_slug', 'lecture_previewable')
    list_filter = ('lecture_previewable', 'lecture_created_at')
    list_per_page = 10
    search_fields = ('lecture_title', 'lecture_description')
    prepopulated_fields = {"lecture_slug": ("lecture_title", )}


class EnrollAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_date')
    list_filter = ('user', 'course', 'enrolled_date')
    list_per_page = 10
    search_fields = ('user', 'course', 'enrolled_date')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'course__course_title')
    list_per_page = 10


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text', 'created_at')
    search_fields = ('text', 'quiz__title')
    list_per_page = 10


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text', 'question__text')
    list_per_page = 10


class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__username', 'course__course_title')
    list_per_page = 10


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lecture', 'created_at')
    search_fields = ('user__username', 'lecture__lecture_title', 'content')
    list_filter = ('created_at',)
    list_per_page = 10


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'course__course_title')
    list_per_page = 10


admin.site.register(Topic, TopicAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(Enroll, EnrollAdmin)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Progress)
admin.site.register(Comment)
admin.site.register(Review)

