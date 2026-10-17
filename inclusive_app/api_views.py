"""JSON API (React frontend uchun). Sessiya + CSRF orqali autentifikatsiya."""
import mimetypes
import os

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers as S
from .forms import CustomUserForm, RegistrationForm
from .models import (
    AmaliyotItem, AmaliyotTuri, Answer, Certificate, Course, CourseEnrollment, CourseTest, KutubxonaCategory,
    KutubxonaItem, Lesson, LessonProgress, News, QuizResult, SahifaRasmi, VideoCategory,
)


def form_errors(form):
    """Django forma xatolarini {maydon: [xabar, ...]} ko'rinishida qaytaradi."""
    return {field: [e['message'] for e in errs] for field, errs in form.errors.get_json_data().items()}


def user_payload(user):
    return S.UserSerializer(user).data if user.is_authenticated else None


# ------------------------------------------------------------------ auth
@method_decorator(ensure_csrf_cookie, name='dispatch')
class MeView(APIView):
    """Joriy foydalanuvchi (yoki null). Shuningdek CSRF cookie'ni o'rnatadi."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'user': user_payload(request.user)})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(request, username=request.data.get('username', ''),
                            password=request.data.get('password', ''))
        if not user:
            return Response({'detail': 'Username yoki parol xato!'}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response({'user': user_payload(user)})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({'ok': True})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        form = RegistrationForm(request.data)
        if not form.is_valid():
            return Response({'errors': form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)
        user = form.save()
        login(request, user)
        return Response({'user': user_payload(user)}, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        form = CustomUserForm(request.data, instance=request.user)
        if not form.is_valid():
            return Response({'errors': form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)
        form.save()
        return Response({'user': user_payload(request.user)})


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = PasswordChangeForm(request.user, request.data)
        if not form.is_valid():
            return Response({'errors': form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)
        user = form.save()
        update_session_auth_hash(request, user)
        return Response({'ok': True})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'user': user_payload(u),
            'certificates': S.CertificateSerializer(
                Certificate.objects.filter(user=u).select_related('course').order_by('-id'), many=True).data,
            'enrollments': S.EnrollmentSerializer(
                CourseEnrollment.objects.filter(user=u).select_related('course').order_by('-enrolled_at'),
                many=True).data,
            'results': S.QuizResultSerializer(
                QuizResult.objects.filter(user=u).select_related('quiz__course').order_by('-completed_at'),
                many=True).data,
        })


# ------------------------------------------------------------------ bosh sahifa / yangiliklar
class HomeView(APIView):
    def get(self, request):
        banners = SahifaRasmi.objects.filter(is_published=True).order_by('-created_at')[:3]
        news = News.objects.filter(is_published=True).order_by('-created_at')
        return Response({'banners': S.BannerSerializer(banners, many=True).data,
                         'news': S.NewsListSerializer(news, many=True).data})


class NewsDetailView(APIView):
    def get(self, request, slug):
        return Response(S.NewsDetailSerializer(get_object_or_404(News, slug=slug, is_published=True)).data)


# ------------------------------------------------------------------ o'qitish amaliyoti
class AmaliyotTurlariView(APIView):
    def get(self, request):
        return Response(S.AmaliyotTuriSerializer(AmaliyotTuri.objects.all(), many=True).data)


class AmaliyotListView(APIView):
    def get(self, request):
        qs = AmaliyotItem.objects.select_related('turi').prefetch_related('sections')
        return Response(S.AmaliyotItemListSerializer(qs, many=True).data)


class AmaliyotTuriView(APIView):
    def get(self, request, slug):
        tur = get_object_or_404(AmaliyotTuri, slug=slug)
        items = tur.items.select_related('turi').prefetch_related('sections').order_by('-created_at')
        return Response({'tur': S.AmaliyotTuriSerializer(tur).data,
                         'items': S.AmaliyotItemListSerializer(items, many=True).data})


class AmaliyotItemView(APIView):
    def get(self, request, tur_slug, item_slug):
        item = get_object_or_404(
            AmaliyotItem.objects.select_related('turi').prefetch_related('sections', 'helps', 'videos'),
            slug=item_slug, turi__slug=tur_slug)
        return Response(S.AmaliyotItemDetailSerializer(item).data)


# ------------------------------------------------------------------ kutubxona / videolar
class KutubxonaView(APIView):
    def get(self, request):
        cats = KutubxonaCategory.objects.all()
        items = KutubxonaItem.objects.filter(is_active=True).select_related('category').order_by('-created_at')
        active = None
        cat_id = request.query_params.get('category')
        if cat_id:
            active = get_object_or_404(KutubxonaCategory, id=cat_id)
            items = items.filter(category=active)
        return Response({'categories': S.KutubxonaCategorySerializer(cats, many=True).data,
                         'items': S.KutubxonaItemSerializer(items, many=True).data,
                         'active_category': active.id if active else None})


class KutubxonaDetailView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(KutubxonaItem.objects.select_related('category'), pk=pk, is_active=True)
        return Response({'item': S.KutubxonaItemSerializer(item).data,
                         'categories': S.KutubxonaCategorySerializer(KutubxonaCategory.objects.all(),
                                                                     many=True).data})


class VideolarView(APIView):
    def get(self, request):
        cats = VideoCategory.objects.prefetch_related('videos').order_by('-name')
        return Response(S.VideoCategorySerializer([c for c in cats if c.videos.all()], many=True).data)


def kutubxona_file_view(request, pk):
    """Word fayllar yuklab olinadi, PDF va boshqalar brauzerda ochiladi."""
    item = get_object_or_404(KutubxonaItem, pk=pk, is_active=True)
    if not item.file:
        raise Http404
    mime_type, _ = mimetypes.guess_type(item.file.name)
    word = ('application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    if mime_type in word:
        return FileResponse(item.file.open('rb'), as_attachment=True, filename=os.path.basename(item.file.name))
    return FileResponse(item.file.open('rb'), content_type=mime_type, as_attachment=False)


@login_required
def download_certificate(request, course_id):
    cert = get_object_or_404(Certificate, user=request.user, course_id=course_id)
    if not cert.pdf:
        raise Http404
    return FileResponse(cert.pdf.open('rb'), as_attachment=True, filename=f"certificate_{cert.course.slug}.pdf")


# ------------------------------------------------------------------ kurslar
class CourseListView(APIView):
    def get(self, request):
        return Response(S.CourseListSerializer(Course.objects.filter(is_active=True), many=True).data)


class CourseDetailView(APIView):
    def get(self, request, slug):
        course = get_object_or_404(Course.objects.prefetch_related('modules__lessons'), slug=slug, is_active=True)
        user = request.user
        enrollment = (CourseEnrollment.objects.filter(user=user, course=course).first()
                      if user.is_authenticated else None)
        done = set()
        if enrollment:
            done = set(LessonProgress.objects.filter(enrollment=enrollment, is_completed=True)
                       .values_list('lesson_id', flat=True))
        quiz = CourseTest.objects.filter(course=course).first()
        result = (QuizResult.objects.filter(user=user, quiz=quiz).first()
                  if quiz and user.is_authenticated else None)

        def file_url(f, unlocked):
            return f.url if (f and unlocked) else None

        modules = []
        for module in course.modules.all():
            lessons = []
            for les in module.lessons.all():
                unlocked = bool(enrollment) or les.is_free
                lessons.append({
                    'id': les.id, 'title': les.title, 'duration': les.duration, 'is_free': les.is_free,
                    'locked': not unlocked, 'completed': les.id in done,
                    'has_video': bool(les.video), 'has_pdf': bool(les.pdf),
                    'video': file_url(les.video, unlocked), 'pdf': file_url(les.pdf, unlocked),
                    'content': les.content if unlocked else '',
                })
            modules.append({'id': module.id, 'title': module.title, 'lessons': lessons})
        return Response({
            'course': S.CourseListSerializer(course).data,
            'modules': modules,
            'enrolled': bool(enrollment),
            'progress': enrollment.progress if enrollment else 0,
            'quiz': {'id': quiz.id, 'title': quiz.title, 'min_percentage': quiz.min_percentage} if quiz else None,
            'quiz_result': S.QuizResultSerializer(result).data if result else None,
        })


class CourseEnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_active=True)
        _, created = CourseEnrollment.objects.get_or_create(user=request.user, course=course)
        return Response({'created': created, 'slug': course.slug})


class LessonCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = get_object_or_404(CourseEnrollment, user=request.user, course=lesson.module.course)
        obj, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        if not obj.is_completed:
            obj.is_completed = True
            obj.completed_at = timezone.now()
            obj.save()
        return Response({'progress': enrollment.get_course_progress()})


# ------------------------------------------------------------------ testlar
def grade(quiz, submitted):
    """submitted: {savol_id: javob_id}. Javob shu savolga tegishli bo'lishi shart."""
    questions = list(quiz.questions.prefetch_related('answers'))
    correct = 0
    for q in questions:
        try:
            chosen = int(submitted.get(str(q.id)))
        except (TypeError, ValueError):
            continue
        if any(a.id == chosen and a.is_correct for a in q.answers.all()):
            correct += 1
    score = int(correct / len(questions) * 100) if questions else 0
    return score, score >= quiz.min_percentage


class QuizListView(APIView):
    def get(self, request):
        return Response(S.QuizListSerializer(CourseTest.objects.select_related('course'), many=True).data)


class QuizDetailView(APIView):
    def get(self, request, quiz_id):
        quiz = get_object_or_404(CourseTest.objects.prefetch_related('questions__answers'), id=quiz_id)
        return Response({'quiz': {'id': quiz.id, 'title': quiz.title, 'min_percentage': quiz.min_percentage},
                         'questions': S.QuestionPublicSerializer(quiz.questions.all(), many=True).data})


class QuizSubmitView(APIView):
    """Mustaqil test: qayta topshirish mumkin (natija yangilanadi)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(CourseTest, id=quiz_id)
        score, passed = grade(quiz, request.data.get('answers') or {})
        result, _ = QuizResult.objects.update_or_create(
            user=request.user, quiz=quiz, defaults={'score': score, 'passed': passed})
        return Response({'result': S.QuizResultSerializer(result).data})


class QuizResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        result = get_object_or_404(QuizResult.objects.select_related('quiz__course'),
                                   user=request.user, quiz_id=quiz_id)
        return Response({'result': S.QuizResultSerializer(result).data})


class CourseTestView(APIView):
    """Kurs yakuniy testi: kurs 100% tugagach, faqat bir marta topshiriladi."""
    permission_classes = [IsAuthenticated]

    def _context(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        enrollment = get_object_or_404(CourseEnrollment, user=request.user, course=course)
        quiz = get_object_or_404(CourseTest, course=course)
        return course, enrollment, quiz

    def get(self, request, course_id):
        course, enrollment, quiz = self._context(request, course_id)
        if enrollment.get_course_progress() < 100:
            return Response({'detail': 'Avval kursni tugating', 'slug': course.slug},
                            status=status.HTTP_403_FORBIDDEN)
        if QuizResult.objects.filter(user=request.user, quiz=quiz).exists():
            return Response({'already_done': True, 'quiz_id': quiz.id})
        return Response({'quiz': {'id': quiz.id, 'title': quiz.title, 'min_percentage': quiz.min_percentage},
                         'questions': S.QuestionPublicSerializer(quiz.questions.prefetch_related('answers'),
                                                                 many=True).data})

    def post(self, request, course_id):
        course, enrollment, quiz = self._context(request, course_id)
        if enrollment.get_course_progress() < 100:
            return Response({'detail': 'Avval kursni tugating', 'slug': course.slug},
                            status=status.HTTP_403_FORBIDDEN)
        if QuizResult.objects.filter(user=request.user, quiz=quiz).exists():
            return Response({'detail': 'Test allaqachon topshirilgan', 'quiz_id': quiz.id},
                            status=status.HTTP_409_CONFLICT)
        score, passed = grade(quiz, request.data.get('answers') or {})
        result = QuizResult.objects.create(user=request.user, quiz=quiz, score=score, passed=passed)
        return Response({'result': S.QuizResultSerializer(result).data}, status=status.HTTP_201_CREATED)
