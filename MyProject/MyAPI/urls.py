from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserView.as_view()), # api để list users
    path('users/<int:pk>/', views.UserDetailView.as_view()), # api để get user
    path('users/<int:pk>/save/posts/', views.SavedPostsView.as_view()), # api để list các post đã save
    path('posts/', views.PostView.as_view()), # api để list post
    path('posts/<int:pk>/', views.SinglePostView.as_view()), # api để get single post
    path('posts/<int:pk>/like/', views.PostLikeView.as_view(), name='post-like'), # api để like post
    path('posts/<int:pk>/save/', views.PostSaveView.as_view(), name='post-save'), # api để save post
    path('posts/<int:pk>/comments/', views.CommentsOfPostView.as_view()), # api để list comments of post
    path('comments/<int:pk>/', views.CommentDetailView.as_view()), # api để get single comment
    path('users/<int:pk>/notifications/', views.NotificationsOfUserView.as_view()),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view()),
    path('posts/nearby/', views.NearbyPostsView.as_view(), name='nearby-posts'), # /api/posts/nearby/?latitude=21.0285&longitude=105.8542&distance=2.0 (latitude, longitude hiện tại, distance là bán kính trong km)
]