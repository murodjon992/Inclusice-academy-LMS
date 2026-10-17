# Inclusive Academy LMS

Django (backend + API) va React (Vite) frontend. Sayt ham, admin panel ham React'da.

```
manage.py, inclusive_talim/, inclusive_app/   Django: modellar, API (api_views.py, admin_api.py)
frontend/src/                                 React kodi: sayt (pages/, components/) va admin panel (admin/)
static/app/                                   React'ning TAYYOR (build qilingan) varianti: app.js, app.css, admin.js
templates/spa.html, admin_spa.html            React'ni yuklaydigan ikki sahifa (sayt va admin)
```

- Sayt: `/`  Admin panel: `/manage-admin/` (faqat superuser, kirish `/login-user/` orqali)
- `/admin/` — Django'ning o'z admin paneli ham o'sha-o'sha turibdi.

---

## 1. Eng oddiy yo'l: shunchaki ishga tushirish (Node kerak EMAS)

Zip ichida React allaqachon tayyorlab qo'yilgan (`static/app/`). Faqat Django kerak:

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # Windows: copy .env.example .env   (ichida DJANGO_SECRET_KEY ni almashtiring)
python manage.py migrate
python manage.py createsuperuser    # admin uchun login/parol
python manage.py runserver
```

Brauzerda http://127.0.0.1:8000 ni oching. Admin: http://127.0.0.1:8000/manage-admin/

Lokal ishlaganda `.env` ichida `DJANGO_DEBUG=True` bo'lsin.

---

## 2. React kodini o'zgartirmoqchi bo'lsangiz (faqat shunda Node kerak)

React kodi (`frontend/src/`) brauzer o'qiy oladigan shaklda emas, uni "build" (tayyorlash) kerak.
Build natijasi `static/app/` papkaga yoziladi, Django shuni foydalanuvchiga beradi.
Ya'ni kodni o'zgartirsangiz, saytda ko'rinishi uchun build qilish shart.

**A) O'zgartirib turib tez ko'rish (ikkita terminal):**

```bash
# 1-terminal (Django)
python manage.py runserver

# 2-terminal (React)
cd frontend
npm install          # faqat birinchi marta
npm run dev
```

http://localhost:5173 ni oching. Kodni saqlasangiz, sahifa o'zi yangilanadi. Admin: http://localhost:5173/manage-admin/

**B) Tugagach, build qilib qo'yish:**

```bash
cd frontend
npm run build        # natija ../static/app/ ga yoziladi
```

Shundan keyin http://127.0.0.1:8000 (Django) yangi variantni ko'rsatadi.

---

## 3. Serverga qo'yish (ideaacademy.uz)

`.env` ni serverda to'ldiring:

```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<yangi uzun tasodifiy kalit>
DJANGO_ALLOWED_HOSTS=ideaacademy.uz
DJANGO_CSRF_TRUSTED_ORIGINS=https://ideaacademy.uz
```

Keyin:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

`collectstatic` nima qiladi: Django `static/` papkasidagi barcha fayllarni (rasm, CSS, JS va React build'i)
bitta `staticfiles/` papkaga yig'adi. Serverda (`DEBUG=False`) Django statik fayllarni o'zi bermaydi,
ularni nginx shu `staticfiles/` papkadan beradi. Lokal ishlaganda bu buyruq kerak emas.
`static/app/` yangilanganda (React qayta build qilinganda) serverda `collectstatic` ni yana bir marta ishga tushiring.

Yuklangan fayllar (`media/`) ham nginx orqali berilishi kerak.

---

## API (`/api/`)

Sessiya + CSRF orqali ishlaydi.

- Sayt: `auth/me|login|logout|register`, `me/profile|password|dashboard`, `home`, `news/<slug>`, `amaliyot-turlari`,
  `amaliyot[/<tur>[/<item>]]`, `kutubxona[/<id>]`, `videolar`, `courses[/<slug>|/<id>/enroll|/<id>/test]`,
  `lessons/<id>/complete`, `quizzes[/<id>|/<id>/submit|/<id>/result]`
- Admin (faqat superuser): `manage/menu`, `manage/dashboard`, `manage/progress`,
  `manage/<bo'lim>/` (ro'yxat, qo'shish), `manage/<bo'lim>/new/` (forma maydonlari), `manage/<bo'lim>/<id>/` (olish, tahrirlash, o'chirish).
  Bo'limlar ro'yxati `inclusive_app/admin_api.py` dagi `RESOURCES` da. Yangi bo'lim qo'shish uchun shu yerga bitta qator qo'shiladi.

## Testlar

```bash
DJANGO_DEBUG=True python manage.py test
```
