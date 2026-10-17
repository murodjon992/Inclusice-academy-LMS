from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
import re
from django.utils.text import slugify
from django.core.exceptions import ValidationError
# Create your models here.
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student','Talaba'),
        ('teacher','O`qituvchi'),
    )
    date_of_birth = models.DateField(null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    university = models.CharField(max_length=100, null=True, blank=True)
    school = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.username

class AmaliyotTuri(models.Model):
    nomi = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nomi)
            slug = base_slug
            counter = 1
            while AmaliyotTuri.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Amaliyot turi"
        verbose_name_plural = "Amaliyot turlari"
    def __str__(self):
        return self.nomi
class AmaliyotItem(models.Model):
    turi = models.ForeignKey(
        AmaliyotTuri,
        related_name='items',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='amaliyot/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while AmaliyotItem.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

class AmaliyotItemHelp(models.Model):
    TYPE_CHOICES = (
        ('pupil', "O‘quvchiga yordam"),
        ('teacher', "O‘qituvchiga yordam"),
    )

    item = models.ForeignKey(
        AmaliyotItem,
        related_name='helps',
        on_delete=models.CASCADE
    )
    help_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text

class AmaliyotVideo(models.Model):
    item = models.ForeignKey(
        AmaliyotItem,
        related_name='videos',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    VIDEO_TYPE_CHOICES = (
        ('url', 'YouTube URL'),
        ('file', 'Fayl Yuklash'),
    )
    video_type = models.CharField(max_length=50, choices=VIDEO_TYPE_CHOICES)
    youtube_url = models.URLField(blank=True,null=True)
    video_file = models.FileField(upload_to='amaliyot/videos/', blank=True, null=True)
    duration = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ['order']

    def embed_url(self):
        from .utils import youtube_embed
        return youtube_embed(self.youtube_url)
    def __str__(self):
        return self.title

class AmaliyotSection(models.Model):
    item = models.ForeignKey(
        AmaliyotItem,
        related_name='sections',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    # In the classroom, Practice toolkit, Resources...
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return f"{self.item.title} - {self.title}"
class RelatedPractice(models.Model):
    from_item = models.ForeignKey(
        AmaliyotItem,
        related_name='related_from',
        on_delete=models.CASCADE
    )
    to_item = models.ForeignKey(
        AmaliyotItem,
        related_name='related_to',
        on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('from_item', 'to_item')
        ordering = ['order']
    def __str__(self):
        return f"{self.from_item} → {self.to_item}"
# ===================================== OXIRIGI O'ZGARISHLAR =====================================
class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    duration = models.PositiveIntegerField(
        help_text="Davomiyligi (soatlarda)"
    )
    is_active = models.BooleanField(default=True)
    has_certificate = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

class CourseModule(models.Model):
    course = models.ForeignKey(
        Course,
        related_name='modules',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return f"{self.course.title} - {self.title}"
class Lesson(models.Model):
    module = models.ForeignKey(
        CourseModule,
        related_name='lessons',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    video = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    pdf = models.FileField(upload_to='lessons/files', blank=True, null=True)
    content = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Dars davomiyligi (daqiqa)")
    order = models.PositiveIntegerField(default=1)
    is_free = models.BooleanField(default=False)  # demo darslar
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title
class CourseEnrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)  # %
    completed = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'course')
    def __str__(self):
        return f"{self.user} - {self.course}"

    def get_course_progress(self):
        total_lessons = Lesson.objects.filter(
            module__course=self.course
        ).count()
        completed_lessons = self.lesson_progress.filter(
            is_completed=True
        ).count()
        if total_lessons == 0:
            return 0
        progress = int((completed_lessons / total_lessons) * 100)
        # 100% bo‘lsa kurs tugadi
        if progress == 100:
            self.completed = True
        self.progress = progress
        self.save(update_fields=['progress', 'completed'])
        return progress
class LessonProgress(models.Model):
    enrollment = models.ForeignKey(
        CourseEnrollment,
        related_name='lesson_progress',
        on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = ('enrollment', 'lesson')
class CourseTest(models.Model):
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    min_percentage = models.PositiveIntegerField(default=70)

    def __str__(self):
        return self.title
class Question(models.Model):
    quiz = models.ForeignKey(
        CourseTest,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    def __str__(self):
        return self.text
class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='test_results', on_delete=models.CASCADE)
    quiz = models.ForeignKey(CourseTest, on_delete=models.CASCADE)
    score = models.FloatField()
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz')
class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    pdf = models.FileField(upload_to='certificates/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user} - {self.course}'
class News(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField(
        help_text="Yangiliklar ro‘yxati uchun qisqa matn"
    )
    content = models.TextField()
    image = models.ImageField(
        upload_to='news/',
        blank=True,
        null=True
    )
    pdf = models.FileField(upload_to='news/', blank=True, null=True)
    youtube_link = models.URLField("Youtube havolasi",blank=True,null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title
class SahifaRasmi(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(
        upload_to='sahifarasm/',
        blank=True,null=True
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
class KutubxonaCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class KutubxonaItem(models.Model):
    RESOURCE_TYPE = (
        ('file', 'Fayl'),
        ('link', 'Tashqi havola'),
    )
    category = models.ForeignKey(KutubxonaCategory, related_name='kitoblar', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    resource_type = models.CharField(
        max_length=10,
        choices=RESOURCE_TYPE,
        default='file'
    )
    file = models.FileField(
        upload_to='library/',
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to='library/',blank=True, null=True)
    external_link = models.URLField(
        "Tashqi sayt havolasi",
        blank=True,
        null=True
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    def clean(self):
        if self.resource_type == 'file' and not self.file:
            raise ValidationError("Fayl yuklashingiz kerak")
        if self.resource_type == 'link' and not self.external_link:
            raise ValidationError("Tashqi havola kiriting")

    def __str__(self):
        return self.title
class VideoCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(unique=True, blank=True, null=True) # URL uchun qulay (masalan: sport-videolari)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while VideoCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Video Kategoriya"
        verbose_name_plural = "Video Kategoriyalar"

class Video(models.Model):
    VIDEO_TYPE_CHOICES = (
        ('url', 'YouTube URL'),
        ('file', 'Fayl Yuklash'),
    )
    category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    title = models.CharField(max_length=255)
    video_type = models.CharField(max_length=10, choices=VIDEO_TYPE_CHOICES)
    youtube_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)

    def embed_url(self):
        from .utils import youtube_embed
        return youtube_embed(self.youtube_url)

    def __str__(self):
        return self.title

# ================================= OXIRIGI O'ZGARISHLAR  OXIRI ==================================