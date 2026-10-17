from django.contrib.auth import logout
from django.shortcuts import redirect, render


def spa(request, *args, **kwargs):
    """Ommaviy sahifalar React ilovasi orqali ko'rsatiladi (templates/spa.html)."""
    return render(request, 'spa.html')


def admin_spa(request, *args, **kwargs):
    """Admin panel ham React ilovasi (templates/admin_spa.html). Ruxsatni API tekshiradi (faqat superuser)."""
    return render(request, 'admin_spa.html')


def user_logout(request):
    logout(request)
    return redirect("inclusive_app:login_user")
