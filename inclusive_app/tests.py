import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import (
    Answer, Certificate, Course, CourseEnrollment, CourseModule, CourseTest, CustomUser, Lesson, News, Question,
    QuizResult,
)
from .admin_api import RESOURCES
from .utils import youtube_embed


class BaseCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('ali', password='Sinov12345!', first_name='Ali', last_name='V',
                                                   user_type='student')
        self.admin = CustomUser.objects.create_superuser('boss', password='Sinov12345!')
        self.course = Course.objects.create(title='Kurs 1', description='d', duration=2)
        mod = CourseModule.objects.create(course=self.course, title='M1')
        self.free = Lesson.objects.create(module=mod, title='Bepul', duration=5, is_free=True, content='x')
        self.paid = Lesson.objects.create(module=mod, title='Pullik', duration=5, content='secret')
        self.quiz = CourseTest.objects.create(course=self.course, title='Test 1', min_percentage=50)
        self.q1 = Question.objects.create(quiz=self.quiz, text='Q1')
        self.q2 = Question.objects.create(quiz=self.quiz, text='Q2')
        self.a1ok = Answer.objects.create(question=self.q1, text='to‘g‘ri', is_correct=True)
        self.a1no = Answer.objects.create(question=self.q1, text='xato')
        self.a2ok = Answer.objects.create(question=self.q2, text='to‘g‘ri', is_correct=True)
        self.a2no = Answer.objects.create(question=self.q2, text='xato')

    def login(self, user='ali'):
        self.assertTrue(self.client.login(username=user, password='Sinov12345!'))


class AuthApiTests(BaseCase):
    def test_me_anonymous_and_csrf_cookie(self):
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.json(), {'user': None})
        self.assertIn('csrftoken', r.cookies)

    def test_login_ok_and_bad(self):
        bad = self.client.post('/api/auth/login/', {'username': 'ali', 'password': 'x'}, content_type='application/json')
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post('/api/auth/login/', {'username': 'ali', 'password': 'Sinov12345!'},
                              content_type='application/json')
        self.assertEqual(ok.json()['user']['username'], 'ali')
        self.assertEqual(self.client.get('/api/auth/me/').json()['user']['username'], 'ali')

    def test_register_validation_and_success(self):
        r = self.client.post('/api/auth/register/', {'username': 'x'}, content_type='application/json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('first_name', r.json()['errors'])
        data = dict(username='yangi', first_name='A', last_name='B', user_type='teacher', school='1-maktab',
                    password1='Sinov12345!', password2='Sinov12345!')
        r = self.client.post('/api/auth/register/', data, content_type='application/json')
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(self.client.get('/api/auth/me/').json()['user']['username'], 'yangi')

    def test_teacher_requires_school(self):
        data = dict(username='t', first_name='A', last_name='B', user_type='teacher',
                    password1='Sinov12345!', password2='Sinov12345!')
        r = self.client.post('/api/auth/register/', data, content_type='application/json')
        self.assertIn('school', r.json()['errors'])

    def test_profile_and_password(self):
        self.login()
        r = self.client.patch('/api/me/profile/', {'first_name': 'Vali', 'last_name': 'V', 'user_type': 'student'},
                              content_type='application/json')
        self.assertEqual(r.json()['user']['first_name'], 'Vali')
        r = self.client.post('/api/me/password/', {'old_password': 'Sinov12345!', 'new_password1': 'Boshqa98765!',
                                                   'new_password2': 'Boshqa98765!'}, content_type='application/json')
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self.client.get('/api/me/dashboard/').status_code, 200)  # sessiya saqlandi

    def test_protected_endpoints_need_login(self):
        for url in ('/api/me/dashboard/', '/api/courses/%d/test/' % self.course.id):
            self.assertIn(self.client.get(url).status_code, (401, 403))


class CourseFlowTests(BaseCase):
    def test_course_list_hides_inactive(self):
        Course.objects.create(title='Yopiq', description='d', duration=1, is_active=False)
        titles = [c['title'] for c in self.client.get('/api/courses/').json()]
        self.assertEqual(titles, ['Kurs 1'])

    def test_lessons_locked_until_enrolled(self):
        d = self.client.get(f'/api/courses/{self.course.slug}/').json()
        paid = [l for m in d['modules'] for l in m['lessons'] if l['title'] == 'Pullik'][0]
        self.assertTrue(paid['locked'])
        self.assertEqual(paid['content'], '')
        self.login()
        self.client.post(f'/api/courses/{self.course.id}/enroll/')
        d = self.client.get(f'/api/courses/{self.course.slug}/').json()
        paid = [l for m in d['modules'] for l in m['lessons'] if l['title'] == 'Pullik'][0]
        self.assertFalse(paid['locked'])
        self.assertEqual(paid['content'], 'secret')

    def test_progress_test_certificate_flow(self):
        self.login()
        self.client.post(f'/api/courses/{self.course.id}/enroll/')
        # kurs tugamaguncha test yopiq
        self.assertEqual(self.client.get(f'/api/courses/{self.course.id}/test/').status_code, 403)
        self.assertEqual(self.client.post(f'/api/lessons/{self.free.id}/complete/').json()['progress'], 50)
        self.assertEqual(self.client.post(f'/api/lessons/{self.paid.id}/complete/').json()['progress'], 100)
        r = self.client.get(f'/api/courses/{self.course.id}/test/').json()
        self.assertNotIn('is_correct', str(r))
        # boshqa savolning to'g'ri javobini yuborish ball bermasligi kerak
        res = self.client.post(f'/api/courses/{self.course.id}/test/', {'answers': {
            str(self.q1.id): self.a2ok.id, str(self.q2.id): self.a2ok.id}}, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['result']['score'], 50)
        # ikkinchi urinish rad etiladi (500 emas)
        again = self.client.post(f'/api/courses/{self.course.id}/test/', {'answers': {}}, content_type='application/json')
        self.assertEqual(again.status_code, 409)

    def test_standalone_quiz_and_certificate(self):
        self.login()
        r = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', {'answers': {
            str(self.q1.id): self.a1ok.id, str(self.q2.id): self.a2ok.id}}, content_type='application/json')
        self.assertTrue(r.json()['result']['passed'])
        self.assertTrue(Certificate.objects.filter(user=self.user, course=self.course).exists())
        # noto'g'ri ID 500 bermasligi kerak
        r = self.client.post(f'/api/quizzes/{self.quiz.id}/submit/', {'answers': {str(self.q1.id): 'abc'}},
                             content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get(f'/api/quizzes/{self.quiz.id}/result/').status_code, 200)

    def test_missing_course_is_404(self):
        self.assertEqual(self.client.get('/api/courses/yoq-kurs/').status_code, 404)


class PublicApiTests(BaseCase):
    def test_home_news_and_embed(self):
        News.objects.create(title='Yangilik', short_description='s', content='c',
                            youtube_link='https://youtu.be/dQw4w9WgXcQ?si=abc')
        News.objects.create(title='Yashirin', short_description='s', content='c', is_published=False)
        d = self.client.get('/api/home/').json()
        self.assertEqual(len(d['news']), 1)
        self.assertEqual(d['news'][0]['embed_url'], 'https://www.youtube.com/embed/dQw4w9WgXcQ')

    def test_youtube_embed_variants(self):
        for u in ('https://www.youtube.com/watch?v=abcdefghijk', 'https://youtu.be/abcdefghijk',
                  'https://www.youtube.com/embed/abcdefghijk'):
            self.assertEqual(youtube_embed(u), 'https://www.youtube.com/embed/abcdefghijk')
        self.assertIsNone(youtube_embed(None))
        self.assertIsNone(youtube_embed('https://example.com'))

    def test_misc_endpoints(self):
        for url in ('/api/amaliyot-turlari/', '/api/amaliyot/', '/api/kutubxona/', '/api/videolar/',
                    '/api/quizzes/', f'/api/quizzes/{self.quiz.id}/'):
            self.assertEqual(self.client.get(url).status_code, 200, url)



def png(name='x.png'):
    buf = io.BytesIO()
    Image.new('RGB', (4, 4), 'purple').save(buf, 'PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class SpaTests(BaseCase):
    def test_spa_routes_serve_react_shell(self):
        for url in ('/', '/kurslar/', '/login-user/', '/course-detail/abc/', '/yoq-sahifa/'):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertContains(r, 'id="root"')
            self.assertContains(r, 'app/app.js')

    def test_admin_shell(self):
        for url in ('/manage-admin/', '/manage-admin/r/courses', '/manage-admin/r/courses/3'):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertContains(r, 'app/admin.js')


@override_settings(DEBUG=True)
class AdminApiTests(BaseCase):
    def setUp(self):
        super().setUp()
        self._media = tempfile.mkdtemp()
        self._ov = override_settings(MEDIA_ROOT=self._media)
        self._ov.enable()
        self.login('boss')

    def tearDown(self):
        self._ov.disable()
        shutil.rmtree(self._media, ignore_errors=True)

    def test_permissions(self):
        self.client.logout()
        for url in ('/api/manage/menu/', '/api/manage/dashboard/', '/api/manage/progress/', '/api/manage/courses/'):
            self.assertIn(self.client.get(url).status_code, (401, 403), url)
        self.login('ali')
        for url in ('/api/manage/menu/', '/api/manage/courses/', '/api/manage/users/'):
            self.assertEqual(self.client.get(url).status_code, 403, url)
        self.assertEqual(self.client.delete(f'/api/manage/courses/{self.course.id}/').status_code, 403)

    def test_menu_dashboard_progress(self):
        menu = self.client.get('/api/manage/menu/').json()
        self.assertEqual(sum(len(g['items']) for g in menu['groups']), len(RESOURCES))
        stats = {s['key']: s['value'] for s in self.client.get('/api/manage/dashboard/').json()['stats']}
        self.assertEqual(stats['users'], 2)
        CourseEnrollment.objects.create(user=self.user, course=self.course)
        rows = self.client.get('/api/manage/progress/').json()['rows']
        self.assertEqual(rows[0]['total'], 2)
        self.assertEqual(rows[0]['progress'], 0)

    def test_every_resource_lists_and_has_schema(self):
        CourseEnrollment.objects.create(user=self.user, course=self.course)
        for res in RESOURCES:
            r = self.client.get(f'/api/manage/{res.key}/')
            self.assertEqual(r.status_code, 200, res.key)
            self.assertTrue(r.json()['columns'], res.key)
            n = self.client.get(f'/api/manage/{res.key}/new/')
            self.assertEqual(n.status_code, 200, res.key)
            self.assertTrue(n.json()['fields'], res.key)
        self.assertEqual(self.client.get('/api/manage/nope/').status_code, 404)

    def test_every_existing_object_opens_for_edit(self):
        CourseEnrollment.objects.create(user=self.user, course=self.course)
        for res in RESOURCES:
            for obj in res.model.objects.all()[:2]:
                r = self.client.get(f'/api/manage/{res.key}/{obj.pk}/')
                self.assertEqual(r.status_code, 200, (res.key, obj.pk))
                self.assertTrue(r.json()['fields'])

    def test_course_crud_with_image(self):
        r = self.client.post('/api/manage/courses/', {'title': 'Yangi kurs', 'description': 'tavsif', 'duration': '45',
                                                       'is_active': 'on', 'image': png()})
        self.assertEqual(r.status_code, 201, r.content)
        cid = r.json()['id']
        d = self.client.get(f'/api/manage/courses/{cid}/').json()
        image = [f for f in d['fields'] if f['name'] == 'image'][0]
        self.assertTrue(image['current'])
        # rasm yuborilmasa, eskisi saqlanadi
        r = self.client.put(f'/api/manage/courses/{cid}/', {'title': 'Nom 2', 'description': 'tavsif', 'duration': '50'},
                            content_type='multipart/form-data; boundary=BoUnDaRy') if False else None
        from django.test.client import encode_multipart
        body = encode_multipart('BoUnDaRy', {'title': 'Nom 2', 'description': 'tavsif', 'duration': '50'})
        r = self.client.put(f'/api/manage/courses/{cid}/', body, content_type='multipart/form-data; boundary=BoUnDaRy')
        self.assertEqual(r.status_code, 200, r.content)
        c = Course.objects.get(id=cid)
        self.assertEqual((c.title, c.duration), ('Nom 2', 50))
        self.assertTrue(c.image)
        self.assertEqual(self.client.delete(f'/api/manage/courses/{cid}/').status_code, 204)
        self.assertFalse(Course.objects.filter(id=cid).exists())

    def test_validation_errors_returned(self):
        r = self.client.post('/api/manage/courses/', {'title': ''})
        self.assertEqual(r.status_code, 400)
        self.assertIn('title', r.json()['errors'])

    def test_news_json_create_and_embed_in_list(self):
        r = self.client.post('/api/manage/news/', {'title': 'Yangilik', 'short_description': 's', 'content': 'c',
                                                    'youtube_link': 'https://youtu.be/abcdefghijk', 'is_published': 'on'})
        self.assertEqual(r.status_code, 201, r.content)
        rows = self.client.get('/api/manage/news/').json()['rows']
        self.assertEqual(rows[0]['youtube'], 'https://www.youtube.com/embed/abcdefghijk')

    def test_video_conditional_validation(self):
        r = self.client.post('/api/manage/videos/', {'title': 'V', 'video_type': 'url'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('youtube_url', r.json()['errors'])
        r = self.client.post('/api/manage/videos/', {'title': 'V', 'video_type': 'url', 'youtube_url': 'https://youtu.be/abcdefghijk'})
        self.assertEqual(r.status_code, 201, r.content)

    def test_answer_edit_keeps_single_correct_rule(self):
        # to'g'ri javobni o'zini tahrirlash xato bermasligi kerak
        from django.test.client import encode_multipart
        body = encode_multipart('B', {'question': str(self.q1.id), 'text': 'yangilandi', 'is_correct': 'on'})
        r = self.client.put(f'/api/manage/answers/{self.a1ok.id}/', body, content_type='multipart/form-data; boundary=B')
        self.assertEqual(r.status_code, 200, r.content)
        # ikkinchi to'g'ri javob esa rad etiladi
        r = self.client.post('/api/manage/answers/', {'question': self.q1.id, 'text': 'yana', 'is_correct': 'on'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('non_field', r.json()['errors'])

    def test_user_create_edit_and_self_delete(self):
        base = {'username': 'yangi', 'first_name': 'A', 'last_name': 'B', 'user_type': 'teacher', 'school': '1-maktab',
                'password1': 'Sinov12345!', 'password2': 'Sinov12345!'}
        r = self.client.post('/api/manage/users/', base)
        self.assertEqual(r.status_code, 201, r.content)
        uid = r.json()['id']
        self.assertTrue(CustomUser.objects.get(id=uid).check_password('Sinov12345!'))
        from django.test.client import encode_multipart
        edit = dict(base, first_name='Boshqa', password1='', password2='')
        r = self.client.put(f'/api/manage/users/{uid}/', encode_multipart('B', edit), content_type='multipart/form-data; boundary=B')
        self.assertEqual(r.status_code, 200, r.content)
        u = CustomUser.objects.get(id=uid)
        self.assertEqual(u.first_name, 'Boshqa')
        self.assertTrue(u.check_password('Sinov12345!'))        # parol o'zgarmadi
        self.assertEqual(self.client.delete(f'/api/manage/users/{self.admin.id}/').status_code, 400)
        self.assertTrue(CustomUser.objects.filter(id=self.admin.id).exists())

    def test_search_and_pagination(self):
        for i in range(30):
            Course.objects.create(title=f'Qidiruv {i}', description='d', duration=1)
        d = self.client.get('/api/manage/courses/?q=Qidiruv').json()
        self.assertEqual(d['count'], 30)
        self.assertEqual(d['pages'], 2)
        self.assertEqual(len(d['rows']), 25)
        self.assertEqual(self.client.get('/api/manage/courses/?q=Qidiruv&page=2').json()['rows'].__len__(), 5)

    def test_related_practice_rule(self):
        from .models import AmaliyotItem, AmaliyotTuri
        t = AmaliyotTuri.objects.create(nomi='T')
        a = AmaliyotItem.objects.create(turi=t, title='A')
        r = self.client.post('/api/manage/amaliyot-related/', {'from_item': a.id, 'to_item': a.id})
        self.assertEqual(r.status_code, 400)
