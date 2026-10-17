"""Admin panel uchun umumiy JSON API.

Har bir resurs (kurs, dars, yangilik ...) mavjud Django ModelForm orqali yoziladi, shuning uchun tekshiruv
qoidalari (clean) oldingi admin panel bilan bir xil. Forma maydonlari formaning o'zidan o'qiladi va React
shu "sxema" bo'yicha formani chizadi.
"""
import datetime

from django import forms
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.fields.files import FieldFile
from django.http import Http404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from . import forms as F
from .models import (
    AmaliyotItem, AmaliyotItemHelp, AmaliyotSection, AmaliyotTuri, AmaliyotVideo, Answer, Certificate, Course,
    CourseEnrollment, CourseModule, CourseTest, CustomUser, KutubxonaCategory, KutubxonaItem, Lesson, News,
    Question, QuizResult, RelatedPractice, SahifaRasmi, Video, VideoCategory,
)
from .utils import youtube_embed

PAGE_SIZE = 25

# Model maydonlarining standart (inglizcha) yorliqlari o'rniga o'zbekchasi. Formada o'z yorlig'i bor maydonlarga tegilmaydi.
LABELS = {
    'title': 'Nomi', 'description': 'Tavsif', 'short_description': 'Qisqa tavsif', 'content': 'Matn', 'text': 'Matn',
    'image': 'Rasm', 'pdf': 'PDF fayl', 'video': 'Video fayl', 'file': 'Fayl', 'duration': 'Davomiyligi',
    'is_active': 'Faol', 'is_published': "E'lon qilingan", 'is_free': 'Bepul dars', 'is_correct': "To'g'ri javob",
    'has_certificate': 'Sertifikat beriladi', 'min_percentage': "O'tish foizi (%)", 'order': 'Tartib raqami',
    'course': 'Kurs', 'module': "Kurs bo'limi", 'quiz': 'Test', 'question': 'Savol', 'user': 'Foydalanuvchi',
    'nomi': 'Nomi', 'name': 'Nomi', 'subtitle': "Qo'shimcha matn", 'category': "Bo'lim", 'turi': 'Amaliyot turi',
    'item': 'Amaliyot', 'help_type': 'Yordam turi', 'video_type': 'Video turi', 'video_file': 'Video fayl',
    'youtube_url': 'YouTube havolasi', 'youtube_link': 'YouTube havolasi', 'external_link': 'Tashqi havola',
    'resource_type': 'Resurs turi', 'from_item': 'Qaysi amaliyot', 'to_item': 'Bog\'lanadigan amaliyot',
    'school': 'Maktab', 'university': 'Universitet', 'username': 'Login', 'first_name': 'Ism', 'last_name': 'Familiya',
    'password1': 'Parol', 'password2': 'Parolni tasdiqlang',
}


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


# ----------------------------------------------------------------- foydalanuvchi formasi
class AdminUserApiForm(F.AdminUserCreateForm):
    """Tahrirlashda parol bo'sh qoldirilsa, eski parol saqlanadi."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = "Bo'sh qoldirsangiz, parol o'zgarmaydi"

    def save(self, commit=True):
        user = super(F.AdminUserCreateForm, self).save(commit=False)
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        if user.user_type == 'teacher':
            user.university = None
        elif user.user_type == 'student':
            user.school = None
        if commit:
            user.save()
        return user


# ----------------------------------------------------------------- resurslar ro'yxati
def _media(o):
    return {'embed_url': youtube_embed(o.youtube_url), 'file': o.video_file.url if o.video_file else None,
            'type': o.video_type}


class Res:
    def __init__(self, key, model, form, title, group, columns, search=(), order='-id', select=(), depends=None,
                 icon='bi-circle'):
        self.key, self.model, self.form, self.title, self.group = key, model, form, title, group
        self.columns, self.search, self.order, self.select = columns, search, order, select
        self.depends = depends or {}
        self.icon = icon

    def queryset(self):
        qs = self.model.objects.all()
        if self.select:
            qs = qs.select_related(*self.select)
        return qs.order_by(self.order)


def col(key, label, kind='text', getter=None):
    return {'key': key, 'label': label, 'kind': kind, 'getter': getter}


VIDEO_DEPENDS = {'youtube_url': ('video_type', 'url'), 'video_file': ('video_type', 'file')}

RESOURCES = [
    Res('quizzes', CourseTest, F.QuizForm, "Testlar", "Testlar bo'limi",
        [col('course', 'Kurs'), col('title', 'Test nomi'), col('min_percentage', "O'tish foizi", 'text', lambda o: f'{o.min_percentage}%')],
        search=('title', 'course__title'), select=('course',)),
    Res('questions', Question, F.QuestionForm, "Savollar", "Testlar bo'limi",
        [col('quiz', 'Test'), col('text', 'Savol')], search=('text', 'quiz__title'), select=('quiz',)),
    Res('answers', Answer, F.AnswerForm, "Savollarga variantlar", "Testlar bo'limi",
        [col('question', 'Savol'), col('text', 'Variant'), col('is_correct', "To'g'ri/Noto'g'ri", 'bool')],
        search=('text', 'question__text'), select=('question',)),
    Res('courses', Course, F.CourseForm, "Kurslar", 'Kurslar',
        [col('title', 'Nomi'), col('duration', 'Davomiyligi', 'text', lambda o: f'{o.duration} min'), col('image', 'Rasmi', 'image')],
        search=('title',)),
    Res('course-modules', CourseModule, F.CourseModuleForm, "Kurs bo'limlari", 'Kurslar',
        [col('course', 'Kurs'), col('title', 'Nomi'), col('order', 'Tartib')], search=('title', 'course__title'),
        select=('course',)),
    Res('lessons', Lesson, F.LessonForm, "Darslar", 'Kurslar',
        [col('module', "Bo'lim"), col('title', 'Nomi'), col('video', 'Video', 'video')], search=('title',),
        select=('module', 'module__course')),
    Res('enrollments', CourseEnrollment, F.CourseEnrollmentForm, "Kursga yozilganlar", 'Kurslar',
        [col('user', 'Foydalanuvchi'), col('course', 'Kurs'), col('progress', 'Holati', 'text', lambda o: f'{o.progress}%'),
         col('completed', 'Yakunlandi', 'bool'), col('enrolled_at', 'Yozilgan vaqt', 'datetime')],
        search=('user__username', 'course__title'), select=('user', 'course')),
    Res('amaliyot-turlari', AmaliyotTuri, F.AmaliyotTuriForm, "Amaliyot turlari", "O'qitish amaliyoti",
        [col('nomi', 'Nomi'), col('slug', 'Slug'), col('created_at', 'Vaqti', 'datetime')], search=('nomi',)),
    Res('amaliyot-items', AmaliyotItem, F.AmaliyotItemForm, "Amaliyotlar", "O'qitish amaliyoti",
        [col('turi', 'Amaliyot turi'), col('title', 'Nomi'), col('image', 'Rasmi', 'image'), col('created_at', 'Vaqti', 'date')],
        search=('title',), select=('turi',)),
    Res('amaliyot-sections', AmaliyotSection, F.AmaliyotSectionForm, "Amaliyot bo'limlari", "O'qitish amaliyoti",
        [col('item', 'Amaliyot'), col('title', 'Nomi')], search=('title',), select=('item',)),
    Res('amaliyot-videos', AmaliyotVideo, F.AmaliyotVideoForm, "Amaliyot videolari", "O'qitish amaliyoti",
        [col('item', 'Amaliyot'), col('title', 'Nomi'), col('media', 'Video', 'media', _media)], search=('title',),
        select=('item',), depends=VIDEO_DEPENDS),
    Res('amaliyot-help', AmaliyotItemHelp, F.AmaliyotItemHelpForm, "Yordam (o'quvchi/o'qituvchi)", "O'qitish amaliyoti",
        [col('help_type', 'Yordam turi', 'text', lambda o: o.get_help_type_display()), col('text', 'Matn')],
        search=('text',), select=('item',)),
    Res('amaliyot-related', RelatedPractice, F.RelatedPracticeForm, "Bog'liq amaliyotlar", "O'qitish amaliyoti",
        [col('name', 'Nomi', 'text', lambda o: str(o))], select=('from_item', 'to_item')),
    Res('kutubxona-categories', KutubxonaCategory, F.KutubxonaCategoryForm, "Kutubxona bo'limlari", 'Kutubxona',
        [col('name', "Bo'lim")], search=('name',)),
    Res('kutubxona-items', KutubxonaItem, F.KutubxonaItemForm, "Kutubxona manbalari", 'Kutubxona',
        [col('category', "Bo'lim"), col('title', 'Nomi'), col('image', 'Rasmi', 'image'), col('file', 'Fayl', 'file'),
         col('created_at', 'Vaqti', 'date')], search=('title',), select=('category',),
        depends={'file': ('resource_type', 'file'), 'external_link': ('resource_type', 'link')}),
    Res('video-categories', VideoCategory, F.VideoCategoryForm, "Video kategoriyalari", 'Videolar',
        [col('name', 'Nomi'), col('slug', 'Slug')], search=('name',)),
    Res('videos', Video, F.VideoForm, "Videolar", 'Videolar',
        [col('title', 'Nomi'), col('category', 'Kategoriya'), col('media', 'Video', 'media', _media)],
        search=('title',), select=('category',), depends=VIDEO_DEPENDS),
    Res('news', News, F.NewsForm, "Yangiliklar", 'Sayt',
        [col('title', 'Nomi'), col('created_at', 'Vaqti', 'datetime'),
         col('youtube', 'Youtube', 'youtube', lambda o: youtube_embed(o.youtube_link)), col('image', 'Rasmi', 'image')],
        search=('title',)),
    Res('banners', SahifaRasmi, F.SahifaRasmiForm, "Bosh sahifa bannerlari", 'Sayt',
        [col('title', 'Nomi'), col('created_at', 'Vaqti', 'datetime'), col('image', 'Rasmi', 'image')], search=('title',)),
    Res('users', CustomUser, AdminUserApiForm, "Foydalanuvchilar", 'Foydalanuvchilar',
        [col('name', 'Ism', 'text', lambda o: f'{o.last_name} {o.first_name}'.strip()), col('username', 'Username'),
         col('user_type', 'Turi', 'text', lambda o: o.get_user_type_display()), col('date_of_birth', "Tug'ilgan sana", 'date')],
        search=('username', 'first_name', 'last_name'),
        depends={'school': ('user_type', 'teacher'), 'university': ('user_type', 'student')}),
]
BY_KEY = {r.key: r for r in RESOURCES}


def get_res(key):
    try:
        return BY_KEY[key]
    except KeyError:
        raise Http404


# ----------------------------------------------------------------- serializatsiya yordamchilari
def cell(obj, c):
    if c['getter']:
        return c['getter'](obj)
    v = getattr(obj, c['key'])
    if isinstance(v, FieldFile):
        return v.url if v else None
    if isinstance(v, (datetime.datetime, datetime.date)):
        return v.isoformat()
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    return str(v)


def row(obj, res):
    d = {'id': obj.pk}
    for c in res.columns:
        d[c['key']] = cell(obj, c)
    return d


def field_type(field):
    w = field.widget
    if isinstance(field, forms.ModelMultipleChoiceField):
        return 'multiselect'
    if isinstance(field, forms.ChoiceField):
        return 'select'
    if isinstance(field, forms.BooleanField):
        return 'checkbox'
    if isinstance(field, forms.ImageField):
        return 'image'
    if isinstance(field, forms.FileField):
        return 'file'
    if isinstance(field, forms.DateTimeField):
        return 'datetime'
    if isinstance(field, forms.DateField):
        return 'date'
    if isinstance(field, (forms.IntegerField, forms.FloatField, forms.DecimalField)):
        return 'number'
    if isinstance(w, forms.PasswordInput):
        return 'password'
    if isinstance(w, forms.Textarea):
        return 'textarea'
    if isinstance(field, forms.EmailField):
        return 'email'
    if isinstance(field, forms.URLField):
        return 'url'
    return 'text'


def plain_value(v, ftype):
    if v is None:
        return '' if ftype not in ('multiselect', 'checkbox') else ([] if ftype == 'multiselect' else False)
    if isinstance(v, FieldFile):
        return ''
    if ftype == 'datetime' and isinstance(v, datetime.datetime):
        return v.strftime('%Y-%m-%dT%H:%M')
    if isinstance(v, (datetime.datetime, datetime.date)):
        return v.isoformat()[:10]
    if ftype == 'multiselect':
        return [str(x.pk if hasattr(x, 'pk') else x) for x in v]
    if ftype == 'checkbox':
        return bool(v)
    if hasattr(v, 'pk'):
        return str(v.pk)
    return str(v) if ftype in ('select', 'text', 'textarea', 'number') else v


def _label(name, field):
    default = name.replace('_', ' ').capitalize()
    if name in LABELS and (not field.label or str(field.label) == default):
        return LABELS[name]
    return str(field.label or default)


def describe(form, res):
    fields = []
    for name, field in form.fields.items():
        ftype = field_type(field)
        item = {
            'name': name, 'label': _label(name, field), 'type': ftype,
            'required': field.required, 'help': str(field.help_text or ''),
        }
        if ftype in ('select', 'multiselect'):
            choices = []
            for value, label in field.choices:
                value = getattr(value, 'value', value)
                if value in ('', None):
                    continue
                choices.append([str(value), str(label)])
            item['choices'] = choices
        if getattr(field, 'max_length', None):
            item['max_length'] = field.max_length
        if name in res.depends:
            item['show_if'] = list(res.depends[name])
        bound = form[name]
        if ftype in ('file', 'image'):
            current = bound.value()
            item['current'] = current.url if isinstance(current, FieldFile) and current else None
            item['value'] = ''
        else:
            item['value'] = plain_value(bound.value(), ftype)
        fields.append(item)
    return fields


def form_errors(form):
    out = {}
    for name, errs in form.errors.get_json_data().items():
        out['non_field' if name == '__all__' else name] = [e['message'] for e in errs]
    return out


# ----------------------------------------------------------------- viewlar
class Base(APIView):
    permission_classes = [IsSuperuser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ResourceListView(Base):
    def get(self, request, key):
        res = get_res(key)
        qs = res.queryset()
        q = request.query_params.get('q', '').strip()
        if q and res.search:
            cond = Q()
            for f in res.search:
                cond |= Q(**{f + '__icontains': q})
            qs = qs.filter(cond)
        try:
            page_no = max(int(request.query_params.get('page', 1)), 1)
        except ValueError:
            page_no = 1
        page = Paginator(qs, PAGE_SIZE).get_page(page_no)
        return Response({
            'key': res.key, 'title': res.title,
            'columns': [{'key': c['key'], 'label': c['label'], 'kind': c['kind']} for c in res.columns],
            'rows': [row(o, res) for o in page.object_list],
            'page': page.number, 'pages': page.paginator.num_pages, 'count': page.paginator.count,
            'searchable': bool(res.search),
        })

    def post(self, request, key):
        res = get_res(key)
        form = res.form(request.data, request.FILES)
        if not form.is_valid():
            return Response({'errors': form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)
        obj = form.save()
        return Response({'id': obj.pk}, status=status.HTTP_201_CREATED)


class ResourceNewView(Base):
    def get(self, request, key):
        res = get_res(key)
        return Response({'key': res.key, 'title': res.title, 'fields': describe(res.form(), res)})


class ResourceDetailView(Base):
    def get(self, request, key, pk):
        res = get_res(key)
        obj = _get(res, pk)
        return Response({'key': res.key, 'title': res.title, 'id': obj.pk, 'label': str(obj),
                         'fields': describe(res.form(instance=obj), res)})

    def put(self, request, key, pk):
        res = get_res(key)
        obj = _get(res, pk)
        form = res.form(request.data, request.FILES, instance=obj)
        if not form.is_valid():
            return Response({'errors': form_errors(form)}, status=status.HTTP_400_BAD_REQUEST)
        obj = form.save()
        return Response({'id': obj.pk})

    def delete(self, request, key, pk):
        res = get_res(key)
        obj = _get(res, pk)
        if res.key == 'users' and obj.pk == request.user.pk:
            return Response({'detail': "O'zingizni o'chirib bo'lmaydi"}, status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _get(res, pk):
    try:
        return res.model.objects.get(pk=pk)
    except res.model.DoesNotExist:
        raise Http404


class MenuView(Base):
    def get(self, request):
        groups = {}
        for r in RESOURCES:
            groups.setdefault(r.group, []).append({'key': r.key, 'title': r.title})
        return Response({'groups': [{'title': g, 'items': items} for g, items in groups.items()]})


class DashboardView(Base):
    def get(self, request):
        return Response({'stats': [
            {'key': 'users', 'label': 'Foydalanuvchilar', 'value': CustomUser.objects.count(), 'icon': 'bi-people'},
            {'key': 'certificates', 'label': 'Sertifikat olganlar', 'value': Certificate.objects.count(), 'icon': 'bi-award'},
            {'key': 'courses', 'label': 'Kurslar', 'value': Course.objects.count(), 'icon': 'bi-journal-text'},
            {'key': 'enrollments', 'label': 'Kursga yozilishlar', 'value': CourseEnrollment.objects.count(), 'icon': 'bi-person-check'},
            {'key': 'results', 'label': 'Topshirilgan testlar', 'value': QuizResult.objects.count(), 'icon': 'bi-clipboard-check'},
            {'key': 'news', 'label': 'Yangiliklar', 'value': News.objects.count(), 'icon': 'bi-newspaper'},
        ]})


class ProgressView(Base):
    """Kurs bo'yicha o'quvchilar jarayoni (eski 'lesson-progress' sahifasi)."""

    def get(self, request):
        totals = dict(Course.objects.annotate(n=Count('modules__lessons')).values_list('id', 'n'))
        enrollments = (CourseEnrollment.objects.select_related('user', 'course')
                       .annotate(done=Count('lesson_progress', filter=Q(lesson_progress__is_completed=True)))
                       .order_by('-id'))
        try:
            page_no = max(int(request.query_params.get('page', 1)), 1)
        except ValueError:
            page_no = 1
        page = Paginator(enrollments, PAGE_SIZE).get_page(page_no)
        rows = []
        for e in page.object_list:
            total = totals.get(e.course_id, 0)
            progress = int(e.done / total * 100) if total else 0
            rows.append({'id': e.id, 'user': e.user.username, 'course': e.course.title, 'completed': e.done,
                         'total': total, 'progress': progress, 'quiz_unlocked': progress == 100})
        return Response({'rows': rows, 'page': page.number, 'pages': page.paginator.num_pages,
                         'count': page.paginator.count})
