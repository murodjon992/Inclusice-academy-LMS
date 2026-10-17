from django.urls import path

from . import admin_api as m
from . import api_views as v

urlpatterns = [
    path('auth/me/', v.MeView.as_view()),
    path('auth/login/', v.LoginView.as_view()),
    path('auth/logout/', v.LogoutView.as_view()),
    path('auth/register/', v.RegisterView.as_view()),
    path('me/profile/', v.ProfileView.as_view()),
    path('me/password/', v.PasswordChangeView.as_view()),
    path('me/dashboard/', v.DashboardView.as_view()),

    path('home/', v.HomeView.as_view()),
    path('news/<slug:slug>/', v.NewsDetailView.as_view()),

    path('amaliyot-turlari/', v.AmaliyotTurlariView.as_view()),
    path('amaliyot/', v.AmaliyotListView.as_view()),
    path('amaliyot/<slug:slug>/', v.AmaliyotTuriView.as_view()),
    path('amaliyot/<slug:tur_slug>/<slug:item_slug>/', v.AmaliyotItemView.as_view()),

    path('kutubxona/', v.KutubxonaView.as_view()),
    path('kutubxona/<int:pk>/', v.KutubxonaDetailView.as_view()),
    path('videolar/', v.VideolarView.as_view()),

    path('courses/', v.CourseListView.as_view()),
    path('courses/<slug:slug>/', v.CourseDetailView.as_view()),
    path('courses/<int:course_id>/enroll/', v.CourseEnrollView.as_view()),
    path('courses/<int:course_id>/test/', v.CourseTestView.as_view()),
    path('lessons/<int:lesson_id>/complete/', v.LessonCompleteView.as_view()),

    path('quizzes/', v.QuizListView.as_view()),
    path('quizzes/<int:quiz_id>/', v.QuizDetailView.as_view()),
    path('quizzes/<int:quiz_id>/submit/', v.QuizSubmitView.as_view()),
    path('quizzes/<int:quiz_id>/result/', v.QuizResultView.as_view()),

    # admin panel API (faqat superuser)
    path('manage/menu/', m.MenuView.as_view()),
    path('manage/dashboard/', m.DashboardView.as_view()),
    path('manage/progress/', m.ProgressView.as_view()),
    path('manage/<slug:key>/', m.ResourceListView.as_view()),
    path('manage/<slug:key>/new/', m.ResourceNewView.as_view()),
    path('manage/<slug:key>/<int:pk>/', m.ResourceDetailView.as_view()),
]
