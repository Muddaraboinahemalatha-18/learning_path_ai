from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid

class User(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=50,)
    password = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Course(models.Model):
    course_name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.course_name


class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic_title = models.CharField(max_length=200)
    content_link = models.URLField()
    order = models.IntegerField()

    def __str__(self):
        return self.topic_title


class Assessment(models.Model):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE)
    total_questions = models.IntegerField(default=10)
    pass_percentage = models.IntegerField(default=70)

    def __str__(self):
        return f"Assessment - {self.topic.topic_title}"


class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1)  # A/B/C/D

    def __str__(self):
        return self.question_text

class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField()
    percentage = models.FloatField()
    passed = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.assessment}"

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.certificate_id)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.course_name}"
