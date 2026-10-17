from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, CourseTest, Question,AmaliyotTuri,SahifaRasmi,News,KutubxonaItem,Course,CourseModule,CourseEnrollment,KutubxonaCategory,Lesson,Answer,AmaliyotItem,AmaliyotSection,AmaliyotVideo,RelatedPractice,Video,VideoCategory,AmaliyotItemHelp
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column,Field, Div
from django.contrib.auth import authenticate

class RegistrationForm(UserCreationForm):

    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'type': 'text'}), required=True)
    first_name = forms.CharField(label='Ismingiz', widget=forms.TextInput(attrs={'type': 'text'}), required=True)
    last_name = forms.CharField(label='Familiyangiz', widget=forms.TextInput(attrs={'type': 'text'}), required=True)
    date_of_birth = forms.DateField(label='Tug`ilgan sana', widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES,label='Foydalanuvchi turi')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'date_of_birth', 'user_type', 'university', 'school',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("username", css_class="col-md-6"),
                Column("email", css_class="col-md-6"),
            ),
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            "school",
            "university",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        # ortiqcha fieldni tozalaymiz
        if user.user_type == "teacher":
            user.university = None
        elif user.user_type == "student":
            user.school = None

        if commit:
            user.save()
        return user


    def clean(self):
        cleaned = super().clean()
        user_type = cleaned.get("user_type")
        school = cleaned.get("school")
        university = cleaned.get("university")

        if user_type == "teacher" and not school:
            self.add_error("school", "O‘qituvchi uchun school majburiy")

        if user_type == "student" and not university:
            self.add_error("university", "Talaba uchun university majburiy")

        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Parollar mos emas")

        return cleaned

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Username yoki parol xato!")

        cleaned_data["user"] = user
        return cleaned_data

class CustomUserForm(forms.ModelForm):
    date_of_birth = forms.DateField(label='Tug`ilgan sana', widget=forms.DateInput(attrs={'type': 'date'}),required=False)
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, label='Foydalanuvchi turi')
    class Meta:
        model = CustomUser
        fields = ['first_name','last_name', 'date_of_birth','user_type']

class AmaliyotTuriForm(forms.ModelForm):
    class Meta:
        model = AmaliyotTuri
        fields = ['nomi']

class AmaliyotItemForm(forms.ModelForm):
    class Meta:
        model = AmaliyotItem
        exclude = ('slug',)

class RelatedPracticeForm(forms.ModelForm):
    class Meta:
        model = RelatedPractice
        fields = ['from_item', 'to_item']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('from_item') == cleaned.get('to_item'):
            raise forms.ValidationError(
                "Bir xil amaliyotni o‘ziga bog‘lab bo‘lmaydi"
            )
        return cleaned

class AmaliyotItemHelpForm(forms.ModelForm):
    class Meta:
            model = AmaliyotItemHelp
            fields = '__all__'


class AmaliyotVideoForm(forms.ModelForm):
    class Meta:
        model = AmaliyotVideo
        fields = ['item','title','video_type','youtube_url','video_file','duration','order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('youtube_url', wrapper_class='url_input'),
            Field('video_file', wrapper_class='file_input'),
            Div(
                Field('youtube_url'),
                css_class='url_input'
            ),

            Div(
                Field('video_file'),
                css_class='file_input'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        video_type = cleaned_data.get("video_type")
        youtube_url = cleaned_data.get("youtube_url")
        video_file = cleaned_data.get("video_file")

        if video_type == "url" and not youtube_url:
            self.add_error("youtube_url", "YouTube link kiriting!")

        if video_type == "file" and not video_file:
            self.add_error("video_file", "Video fayl yuklang!")

        return cleaned_data

class AmaliyotSectionForm(forms.ModelForm):
    class Meta:
        model = AmaliyotSection
        fields = '__all__'

class AdminUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Parol', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Parol tasdiqlash', widget=forms.PasswordInput)

    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        label='Foydalanuvchi turi'
    )
    date_of_birth = forms.DateField(label='Tug`ilgan sana', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name','date_of_birth', 'user_type', 'university','school', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("username", css_class="col-md-6"),
                Column("email", css_class="col-md-6"),
            ),
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            "user_type",
            "school",
            "university",
            "password1",
            "password2",
        )


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])


        if user.user_type == "teacher":
            user.university = None
        elif user.user_type == "student":
            user.school = None

        if commit:
            user.save()
        return user

    def clean(self):
        cleaned = super().clean()
        user_type = cleaned.get("user_type")
        school = cleaned.get("school")
        university = cleaned.get("university")

        if user_type == "teacher" and not school:
            self.add_error("school", "O‘qituvchi uchun school majburiy")

        if user_type == "student" and not university:
            self.add_error("university", "Talaba uchun university majburiy")

        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Parollar mos emas")

        return cleaned

class SahifaRasmiForm(forms.ModelForm):
    class Meta:
        model = SahifaRasmi
        fields = '__all__'

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('slug',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 8}),
        }

class KutubxonaItemForm(forms.ModelForm):
    class Meta:
        model = KutubxonaItem
        fields = ['category', 'title','resource_type','file','external_link','image','description']

class KutubxonaCategoryForm(forms.ModelForm):
    class Meta:
        model = KutubxonaCategory
        fields = '__all__'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ('slug',)

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'

class CourseModuleForm(forms.ModelForm):
    class Meta:
        model = CourseModule
        fields = '__all__'

class CourseEnrollmentForm(forms.ModelForm):
    class Meta:
        model = CourseEnrollment
        fields = ['user', 'course']


class QuizForm(forms.ModelForm):
    class Meta:
        model = CourseTest
        fields = '__all__'

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        question = cleaned_data.get('question')
        is_correct = cleaned_data.get('is_correct')

        if is_correct and Answer.objects.filter(
            question=question,
            is_correct=True
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Bu savol uchun allaqachon to‘g‘ri javob mavjud!"
            )

        return  cleaned_data

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['category','title', 'video_type', 'youtube_url', 'video_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('youtube_url', wrapper_class='url_input'),
            Field('video_file', wrapper_class='file_input'),
            Div(
                Field('youtube_url'),
                css_class='url_input'
            ),

            Div(
                Field('video_file'),
                css_class='file_input'
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        video_type = cleaned_data.get("video_type")
        url = cleaned_data.get("youtube_url")
        file = cleaned_data.get("video_file")

        if video_type == 'url' and not url:
            self.add_error('youtube_url', 'YouTube URL required')

        if video_type == 'file' and not file:
            self.add_error('video_file', 'Video file required')

        if video_type == 'url':
            cleaned_data['video_file'] = None

        if video_type == 'file':
            cleaned_data['youtube_url'] = None

        return cleaned_data

class VideoCategoryForm(forms.ModelForm):
    class Meta:
        model = VideoCategory
        exclude = ('slug',)