from django.shortcuts import render
from rest_framework import generics
from .models import Users, Posts, Comments, Notifications
from .serializers import UsersSerializer, PostsSerializer, CommentsSerializer, NotificationsSerializer

# Create your views here.
class UserView(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    
class PostView(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    
class SinglePostView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer