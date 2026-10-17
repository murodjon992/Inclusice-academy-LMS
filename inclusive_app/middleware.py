from django.shortcuts import render
from django.urls import reverse

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 1. ENG MUHIMI: Static va Media fayllarga umuman teginmaymiz!
        if 'static' in path or 'media' in path:
            return self.get_response(request)

        # 2. Custom admin dashboardingiz URL nomi (urls.py dagi name='manage-admin')
        try:
            admin_url = reverse('manage-admin')
        except:
            admin_url = '/manage-admin/' # Agar name bo'lmasa, matn ko'rinishida

        # 3. Agar so'rov admin panelga yoki login sahifasiga bo'lsa, yo'lni to'smaymiz
        if path.startswith(admin_url) or 'login' in path:
            return self.get_response(request)

        # 4. Agar tizimga kirgan user admin (superuser) bo'lsa, unga ham hamma sahifalarni ochamiz
        if request.user.is_authenticated and request.user.is_superuser:
            return self.get_response(request)

        # 5. Qolgan barcha holatlarda (oddiy foydalanuvchilarga) oq xabar chiqadi
        return render(request, 'maintenance.html', status=503)