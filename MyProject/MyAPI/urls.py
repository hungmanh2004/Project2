from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserView.as_view()),
    path('users/<int:pk>/', views.UserDetailView.as_view()),
    path('posts/', views.PostView.as_view()),
    path('posts/<int:pk>/', views.SinglePostView.as_view()),
    path('posts/<int:pk>/comments/', views.CommentsOfPostView.as_view()),
    path('comments/<int:pk>/', views.CommentDetailView.as_view()),
    path('users/<int:pk>/notifications/', views.NotificationsOfUserView.as_view()),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view()),
]