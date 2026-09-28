from django.shortcuts import render, redirect, get_object_or_404
from .models import User, OTP
from .utils import generate_otp, send_otp_email
from .models import Course, Enrollment, Topic, UserScore, Assessment, Question, Certificate, Feedback
from django.core.mail import send_mail
from django.conf import settings
from .certificates import generate_certificate_pdf

def landing(request):
    return render(request, 'landing.html')


def signup(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        user = User(
            full_name=full_name,
            email=email,
            username=username
        )
        user.set_password(password)
        user.save()

        otp_code = generate_otp()
        OTP.objects.create(user=user, otp_code=otp_code)

        send_otp_email(email, otp_code)

        return redirect('verify_otp')

    return render(request, 'auth/signup.html')


def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST['otp']

        otp_obj = OTP.objects.filter(otp_code=otp_entered).last()
        if otp_obj:
            user = otp_obj.user
            user.is_verified = True
            user.save()
            otp_obj.delete()

            return render(request, 'auth/success.html')

        return render(request, 'auth/verify_otp.html', {
            'error': 'Invalid OTP'
        })

    return render(request, 'auth/verify_otp.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
            if user.check_password(password) and user.is_verified:
                request.session['user_id'] = user.id
                return redirect('courses')
        except:
            pass

        return render(request, 'auth/login.html', {
            'error': 'Invalid credentials'
        })

    return render(request, 'auth/login.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        user = User.objects.get(email=email)
        otp_code = generate_otp()

        OTP.objects.create(user=user, otp_code=otp_code)
        send_otp_email(email, otp_code)

        request.session['reset_user'] = user.id
        return redirect('reset_password')

    return render(request, 'auth/forgot_password.html')


def reset_password(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if new_password != confirm_password:
            return render(request, 'auth/reset_password.html', {
                'error': 'Passwords do not match'
            })

        otp_obj = OTP.objects.filter(otp_code=otp).last()
        if otp_obj:
            user = otp_obj.user
            user.set_password(new_password)
            user.save()
            otp_obj.delete()

            return redirect('login')

        return render(request, 'auth/reset_password.html', {
            'error': 'Invalid OTP'
        })

    return render(request, 'auth/reset_password.html')

def courses(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    all_courses = Course.objects.filter(is_active=True)
    return render(request, 'user/courses.html', {
        'courses': all_courses
    })


def enroll_course(request, course_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    course = Course.objects.get(id=course_id)

    Enrollment.objects.get_or_create(user=user, course=course)

    send_mail(
        subject="Course Enrollment Successful",
        message=f"""
Dear {user.username},

You have successfully enrolled in the {course.course_name} course.
You can now start learning your course.

Best Wishes,
AI Learning Platform
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False
    )

    return redirect('topics', course_id=course.id)


def topics(request, course_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    course = Course.objects.get(id=course_id)

    topics = Topic.objects.filter(course=course).order_by('order')

    unlocked_topics = []

    for index, topic in enumerate(topics):
        if index == 0:
            unlocked_topics.append((topic, True))
        else:
            prev_topic = topics[index - 1]
            try:
                score = UserScore.objects.get(
                    user=user,
                    assessment__topic=prev_topic
                )
                unlocked_topics.append((topic, score.passed))
            except:
                unlocked_topics.append((topic, False))

    return render(request, 'user/topics.html', {
        'course': course,
        'topics': unlocked_topics
    })

def topic_content(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    assessment = Assessment.objects.get(topic=topic)

    return render(request, 'user/topic_content.html', {
        'topic': topic,
        'assessment': assessment
    })


def start_assessment(request, assessment_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    assessment = Assessment.objects.get(id=assessment_id)
    questions = Question.objects.filter(assessment=assessment)

    return render(request, 'user/assessment.html', {
        'assessment': assessment,
        'questions': questions
    })


def submit_assessment(request, assessment_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    assessment = Assessment.objects.get(id=assessment_id)
    questions = Question.objects.filter(assessment=assessment)

    score = 0

    for q in questions:
        selected = request.POST.get(str(q.id))
        if selected == q.correct_option:
            score += 1

    percentage = (score / assessment.total_questions) * 100
    passed = percentage >= assessment.pass_percentage

    user_score, created = UserScore.objects.get_or_create(
        user=user,
        assessment=assessment,
        defaults={
            'score': score,
            'percentage': percentage,
            'passed': passed
        }
    )

    if not created:
        user_score.attempt_count += 1
        user_score.score = score
        user_score.percentage = percentage
        user_score.passed = passed
        user_score.save()

    return render(request, 'user/result.html', {
        'score': score,
        'percentage': percentage,
        'passed': passed,
        'assessment': assessment
    })

def scoreboard(request, course_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    course = Course.objects.get(id=course_id)

    assessments = Assessment.objects.filter(topic__course=course)
    scores = UserScore.objects.filter(user=user, assessment__in=assessments)

    if scores.count() != assessments.count():
        return render(request, 'user/scoreboard.html', {
            'error': 'Complete all assessments to view scoreboard'
        })

    for s in scores:
        if not s.passed:
            return render(request, 'user/scoreboard.html', {
                'error': 'Scoreboard visible only if all scores ≥ 70%'
            })

    return render(request, 'user/scoreboard.html', {
        'scores': scores,
        'course': course,
        'eligible': True
    })


def generate_certificate(request, course_id):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    course = get_object_or_404(Course, id=course_id)

    certificate, created = Certificate.objects.get_or_create(
        user=user,
        course=course
    )

    # ✅ NOW MATCHES FUNCTION SIGNATURE
    generate_certificate_pdf(
        user,
        course,
        certificate.certificate_id
    )

    return render(request, 'user/certificate.html', {
        'certificate': certificate
    })

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username == 'admin' and password == 'admin':
            request.session['admin'] = True
            return redirect('admin_dashboard')

        return render(request, 'admin/admin_login.html', {
            'error': 'Invalid admin credentials'
        })

    return render(request, 'admin/admin_login.html')


def admin_dashboard(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    users = User.objects.all()
    enrollments = Enrollment.objects.all()
    scores = UserScore.objects.all()
    feedbacks = Feedback.objects.all()

    return render(request, 'admin/dashboard.html', {
        'users': users,
        'enrollments': enrollments,
        'scores': scores,
        'feedbacks': feedbacks
    })

def submit_feedback(request, course_id):
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    course = Course.objects.get(id=course_id)

    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST['comment']

        Feedback.objects.create(
            user=user,
            course=course,
            rating=rating,
            comment=comment
        )

        return redirect('courses')

    return render(request, 'user/feedback.html', {'course': course})


def add_question(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    courses = Course.objects.all()
    selected_course = None
    assessments = []

    if request.method == 'POST':
        # Step 1: Course selected
        if 'course' in request.POST and 'question_text' not in request.POST:
            course_id = request.POST['course']
            selected_course = Course.objects.get(id=course_id)

            topics = Topic.objects.filter(course=selected_course)
            assessments = Assessment.objects.filter(topic__in=topics)

        # Step 2: Question submitted
        elif 'question_text' in request.POST:
            course_id = request.POST['course']
            assessment_id = request.POST['assessment']

            selected_course = Course.objects.get(id=course_id)
            assessment = Assessment.objects.get(id=assessment_id)

            Question.objects.create(
                assessment=assessment,
                question_text=request.POST['question_text'],
                option_a=request.POST['option_a'],
                option_b=request.POST['option_b'],
                option_c=request.POST['option_c'],
                option_d=request.POST['option_d'],
                correct_option=request.POST['correct_option']
            )

            topics = Topic.objects.filter(course=selected_course)
            assessments = Assessment.objects.filter(topic__in=topics)

            return render(request, 'admin/add_question.html', {
                'courses': courses,
                'selected_course': selected_course,
                'assessments': assessments,
                'success': 'Question added successfully'
            })

    return render(request, 'admin/add_question.html', {
        'courses': courses,
        'selected_course': selected_course,
        'assessments': assessments
    })



def add_course(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    if request.method == 'POST':
        course_name = request.POST['course_name']
        description = request.POST['description']

        Course.objects.create(
            course_name=course_name,
            description=description
        )

        return render(request, 'admin/add_course.html', {
            'success': 'Course added successfully'
        })

    return render(request, 'admin/add_course.html')


def add_assessment(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    courses = Course.objects.all()
    selected_course = None
    topics = []

    if request.method == 'POST':
        # Step 1: Course selected
        if 'course' in request.POST and 'topic' not in request.POST:
            course_id = request.POST['course']
            selected_course = Course.objects.get(id=course_id)
            topics = Topic.objects.filter(course=selected_course)

        # Step 2: Assessment creation
        elif 'topic' in request.POST:
            course_id = request.POST['course']
            topic_id = request.POST['topic']

            selected_course = Course.objects.get(id=course_id)
            topic = Topic.objects.get(id=topic_id)

            # Avoid duplicate assessment
            Assessment.objects.get_or_create(topic=topic)

            topics = Topic.objects.filter(course=selected_course)

            return render(request, 'admin/add_assessment.html', {
                'courses': courses,
                'selected_course': selected_course,
                'topics': topics,
                'success': 'Assessment created successfully'
            })

    return render(request, 'admin/add_assessment.html', {
        'courses': courses,
        'selected_course': selected_course,
        'topics': topics
    })

def add_topic(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    courses = Course.objects.all()
    selected_course = None

    if request.method == 'POST':
        # Step 1: Course selected
        if 'course' in request.POST and 'topic_title' not in request.POST:
            course_id = request.POST['course']
            selected_course = Course.objects.get(id=course_id)

        # Step 2: Topic creation
        elif 'topic_title' in request.POST:
            course_id = request.POST['course']
            topic_title = request.POST['topic_title']
            content_link = request.POST['content_link']
            order = request.POST['order']

            selected_course = Course.objects.get(id=course_id)

            Topic.objects.create(
                course=selected_course,
                topic_title=topic_title,
                content_link=content_link,
                order=order
            )

            return render(request, 'admin/add_topic.html', {
                'courses': courses,
                'selected_course': selected_course,
                'success': 'Topic added successfully'
            })

    return render(request, 'admin/add_topic.html', {
        'courses': courses,
        'selected_course': selected_course
    })


def manage_courses(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    courses = Course.objects.all()
    return render(request, 'admin/manage_courses.html', {'courses': courses})


def delete_course(request, course_id):
    Course.objects.filter(id=course_id).delete()
    return redirect('manage_courses')

def manage_topics(request):
    topics = Topic.objects.select_related('course')
    return render(request, 'admin/manage_topics.html', {'topics': topics})


def delete_topic(request, topic_id):
    Topic.objects.filter(id=topic_id).delete()
    return redirect('manage_topics')


def manage_assessments(request):
    assessments = Assessment.objects.select_related('topic')
    return render(request, 'admin/manage_assessments.html', {'assessments': assessments})


def delete_assessment(request, assessment_id):
    Assessment.objects.filter(id=assessment_id).delete()
    return redirect('manage_assessments')


def manage_questions(request):
    questions = Question.objects.select_related('assessment__topic')
    return render(request, 'admin/manage_questions.html', {'questions': questions})


def delete_question(request, question_id):
    Question.objects.filter(id=question_id).delete()
    return redirect('manage_questions')

def manage_users(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    users = User.objects.all().order_by('-id')
    return render(request, 'admin/manage_users.html', {
        'users': users
    })


def delete_user(request, user_id):
    if not request.session.get('admin'):
        return redirect('admin_login')

    User.objects.filter(id=user_id).delete()
    return redirect('manage_users')