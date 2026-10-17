from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import  Certificate,QuizResult
from .utils import fill_certificate
import os


@receiver(post_save, sender=QuizResult)
def create_certificate_after_test(sender, instance, created, **kwargs):
    # 'created' tekshiruvini olib tashlaymiz, chunki update bo'lganda ham o'tgan bo'lishi mumkin
    if not instance.passed:
        return

    # Allaqachon sertifikat borligini tekshirish (bu qism to'g'ri)
    if Certificate.objects.filter(user=instance.user, course=instance.quiz.course).exists():
        return

    # Sertifikat yaratish
    cert = Certificate.objects.create(
        user=instance.user,
        course=instance.quiz.course,
        score=instance.score
    )

    # PDF generatsiya (bu qismni alohida try-except ichiga olish xavfsizroq)
    try:
        template_path = settings.BASE_DIR / 'static/certificates/inc_sertifikat.pdf'
        # Media papkasi borligini tekshirish
        cert_dir = settings.MEDIA_ROOT / 'certificates'
        cert_dir.mkdir(parents=True, exist_ok=True)

        output_filename = f'certificates/cert_{cert.id}.pdf'
        output_path = settings.MEDIA_ROOT / output_filename

        fill_certificate(
            template_path=template_path,
            output_path=output_path,
            user=instance.user,
            test_name=instance.quiz.title
        )

        # Sertifikat modelini yangilash
        cert.pdf.name = output_filename
        cert.save()
    except Exception as e:
        print(f"PDF yaratishda xato: {e}")
