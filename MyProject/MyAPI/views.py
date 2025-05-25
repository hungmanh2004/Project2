from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Users, Posts, Comments, Notifications
from .serializers import UsersSerializer, PostsSerializer, CommentsSerializer, NotificationsSerializer

# Create your views here.
class UserView(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    
class PostView(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    
class SinglePostView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    
class CommentsOfPostView(generics.ListCreateAPIView):
    serializer_class = CommentsSerializer
    
    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        return Comments.objects.filter(post_id=post_id)
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('pk')
        post = Posts.objects.get(pk=post_id)
        serializer.save(post_id=post)
    
    def create(self, request, *args, **kwargs):
        # Create a mutable copy of the request data
        data = request.data.copy()
        # Remove post_id from request data if it exists (it will be set from URL)
        data.pop('post_id', None)
        # Create a serializer with the modified data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    
class NotificationsOfUserView(generics.ListAPIView):
    serializer_class = NotificationsSerializer
    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        return Notifications.objects.filter(user_id=user_id)
    
    def perform_create(self, serializer):
        user_id = self.kwargs.get('pk')
        user = Users.objects.get(pk=user_id)
        serializer.save(user_id=user)
    
    def create(self, request, *args, **kwargs):
        # Create a mutable copy of the request data
        data = request.data.copy()
        # Remove user_id from request data if it exists (it will be set from URL)
        data.pop('user_id', None)
        # Create a serializer with the modified data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class NotificationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Notifications.objects.all()
    serializer_class = NotificationsSerializer
