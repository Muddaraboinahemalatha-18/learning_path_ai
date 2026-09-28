from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('signup/', views.signup, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('courses/', views.courses, name='courses'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll'),
    path('topics/<int:course_id>/', views.topics, name='topics'),
    path('topic/<int:topic_id>/', views.topic_content, name='topic_content'),
    path('assessment/<int:assessment_id>/', views.start_assessment, name='start_assessment'),
    path('assessment/<int:assessment_id>/submit/', views.submit_assessment, name='submit_assessment'),
    path('scoreboard/<int:course_id>/', views.scoreboard, name='scoreboard'),
    path('certificate/<int:course_id>/', views.generate_certificate, name='generate_certificate'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('feedback/<int:course_id>/', views.submit_feedback, name='feedback'),
    path('add-question/', views.add_question, name='add_question'),
    path('add-course/', views.add_course, name='add_course'),
    path('add-assessment/', views.add_assessment, name='add_assessment'),
    path('add-topic/', views.add_topic, name='add_topic'),
    path('manage-courses/', views.manage_courses, name='manage_courses'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),

    path('manage-topics/', views.manage_topics, name='manage_topics'),
path('delete-topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),

path('manage-assessments/', views.manage_assessments, name='manage_assessments'),
path('delete-assessment/<int:assessment_id>/', views.delete_assessment, name='delete_assessment'),

path('manage-questions/', views.manage_questions, name='manage_questions'),
path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
path('manage-users/', views.manage_users, name='manage_users'),
path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

]
