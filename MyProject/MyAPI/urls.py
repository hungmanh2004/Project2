from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserView.as_view()),
    path('users/<int:pk>/', views.UserView.as_view()),
    path('posts/', views.PostView.as_view()),
    path('posts/<int:pk>/', views.SinglePostView.as_view()),
    # path('comments/', views.CommentView.as_view(), name='comment-list'),
    # path('comments/<int:pk>/', views.CommentView.as_view(), name='comment-detail'),
    # path('notifications/', views.NotificationView.as_view(), name='notification-list'),
    # path('notifications/<int:pk>/', views.NotificationView.as_view(), name='notification-detail'),
]    