"""React frontend uchun JSON serializerlar.

Fayl/rasm maydonlari nisbiy URL (/media/...) bo'lib qaytadi, shuning uchun sayt qaysi
domen ostida ishlamasin (ideaacademy.uz, localhost, Vite proxy) havolalar buzilmaydi.
"""
from django.db import models
from rest_framework import serializers

from .models import (
    AmaliyotItem, AmaliyotItemHelp, AmaliyotSection, AmaliyotTuri, AmaliyotVideo, Certificate, Course,
    CourseEnrollment, CourseModule, CourseTest, CustomUser, KutubxonaCategory, KutubxonaItem, Lesson, News,
    Question, Answer, QuizResult, SahifaRasmi, Video, VideoCategory,
)
from .utils import youtube_embed


class RelFileField(serializers.FileField):
    def to_representation(self, value):
        return value.url if value else None


class Base(serializers.ModelSerializer):
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        models.FileField: RelFileField,
        models.ImageField: RelFileField,
    }


class UserSerializer(Base):
    is_admin = serializers.BooleanField(source='is_superuser', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'date_of_birth', 'user_type',
                  'university', 'school', 'is_admin')


class BannerSerializer(Base):
    class Meta:
        model = SahifaRasmi
        fields = ('id', 'title', 'subtitle', 'image')


class NewsListSerializer(Base):
    embed_url = serializers.SerializerMethodField()

    def get_embed_url(self, obj):
        return youtube_embed(obj.youtube_link)

    class Meta:
        model = News
        fields = ('id', 'title', 'slug', 'short_description', 'image', 'pdf', 'embed_url', 'created_at')


class NewsDetailSerializer(NewsListSerializer):
    class Meta(NewsListSerializer.Meta):
        fields = NewsListSerializer.Meta.fields + ('content',)


# ---------- amaliyot ----------
class AmaliyotTuriSerializer(Base):
    class Meta:
        model = AmaliyotTuri
        fields = ('id', 'nomi', 'slug')


class SectionSerializer(Base):
    class Meta:
        model = AmaliyotSection
        fields = ('id', 'title', 'content')


class HelpSerializer(Base):
    class Meta:
        model = AmaliyotItemHelp
        fields = ('id', 'help_type', 'text')


class AmaliyotVideoSerializer(Base):
    embed_url = serializers.SerializerMethodField()

    def get_embed_url(self, obj):
        return youtube_embed(obj.youtube_url)

    class Meta:
        model = AmaliyotVideo
        fields = ('id', 'title', 'video_type', 'embed_url', 'video_file', 'duration', 'description')


class AmaliyotItemListSerializer(Base):
    turi = AmaliyotTuriSerializer(read_only=True)
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = AmaliyotItem
        fields = ('id', 'title', 'slug', 'image', 'turi', 'sections')


class AmaliyotItemDetailSerializer(AmaliyotItemListSerializer):
    helps = HelpSerializer(many=True, read_only=True)
    videos = AmaliyotVideoSerializer(many=True, read_only=True)
    related = serializers.SerializerMethodField()

    def get_related(self, obj):
        rel = obj.related_from.select_related('to_item__turi')
        return [{'title': r.to_item.title, 'slug': r.to_item.slug, 'tur_slug': r.to_item.turi.slug,
                 'image': r.to_item.image.url if r.to_item.image else None} for r in rel]

    class Meta(AmaliyotItemListSerializer.Meta):
        fields = AmaliyotItemListSerializer.Meta.fields + ('description', 'helps', 'videos', 'related')


# ---------- kutubxona / video ----------
class KutubxonaCategorySerializer(Base):
    class Meta:
        model = KutubxonaCategory
        fields = ('id', 'name')


class KutubxonaItemSerializer(Base):
    category = KutubxonaCategorySerializer(read_only=True)

    class Meta:
        model = KutubxonaItem
        fields = ('id', 'title', 'resource_type', 'file', 'image', 'external_link', 'description',
                  'created_at', 'category')


class VideoSerializer(Base):
    embed_url = serializers.SerializerMethodField()

    def get_embed_url(self, obj):
        return youtube_embed(obj.youtube_url)

    class Meta:
        model = Video
        fields = ('id', 'title', 'video_type', 'embed_url', 'video_file')


class VideoCategorySerializer(Base):
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = VideoCategory
        fields = ('id', 'name', 'slug', 'videos')


# ---------- kurslar / testlar ----------
class CourseListSerializer(Base):
    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'image', 'duration', 'has_certificate')


class QuizListSerializer(Base):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = CourseTest
        fields = ('id', 'title', 'image', 'min_percentage', 'course_title')


class AnswerPublicSerializer(Base):
    class Meta:
        model = Answer
        fields = ('id', 'text')          # is_correct hech qachon yuborilmaydi


class QuestionPublicSerializer(Base):
    answers = AnswerPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'answers')


class QuizResultSerializer(Base):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    course_slug = serializers.CharField(source='quiz.course.slug', read_only=True)

    class Meta:
        model = QuizResult
        fields = ('id', 'quiz', 'quiz_title', 'course_slug', 'score', 'passed', 'completed_at')


class CertificateSerializer(Base):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_id = serializers.IntegerField(read_only=True)
    pdf = serializers.SerializerMethodField()

    def get_pdf(self, obj):
        return obj.pdf.url if obj.pdf else None

    class Meta:
        model = Certificate
        fields = ('id', 'course_id', 'course_title', 'score', 'pdf', 'created_at')


class EnrollmentSerializer(Base):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = ('id', 'course_title', 'course_slug', 'progress', 'completed', 'enrolled_at')
