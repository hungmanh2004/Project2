from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view # import sẵn thôi chứ chưa cần lắm
from rest_framework.response import Response
from .models import Users, Posts, Comments, Notifications, PostLike, PostSave
from .serializers import UsersSerializer, PostsSerializer, CommentsSerializer, NotificationsSerializer, PostLikeSerializer, PostSaveSerializer
from rest_framework.permissions import IsAuthenticated # import sẵn thôi chứ chưa cần lắm
from rest_framework.decorators import permission_classes # import sẵn thôi chứ chưa cần lắm
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

# Create your views here.
class UserView(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username']
    ordering_fields = ['user_id','username']
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    
class PostView(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['description']
    ordering_fields = ['post_time']
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
class SinglePostView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class PostLikeView(generics.CreateAPIView):
    serializer_class = PostLikeSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post_id'] = self.kwargs.get('pk')
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        status_code = status.HTTP_201_CREATED if result['liked'] else status.HTTP_200_OK
        return Response(result, status=status_code)
    
class PostSaveView(generics.CreateAPIView):
    serializer_class = PostSaveSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post_id'] = self.kwargs.get('pk')
        return context
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        status_code = status.HTTP_201_CREATED if result['saved'] else status.HTTP_200_OK
        return Response(result, status=status_code)


class SavedPostsView(generics.ListAPIView):
    serializer_class = PostsSerializer
    
    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        saved_posts = PostSave.objects.filter(user_id=user_id).values_list('post_id', flat=True)
        return Posts.objects.filter(post_id__in=saved_posts)


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
        # Mark all as read trước khi trả về danh sách
        Notifications.objects.filter(user_id=user_id, read_status=False).update(read_status=True)
        return Notifications.objects.filter(user_id=user_id)
    
    def perform_create(self, serializer):
        user_id = self.kwargs.get('pk')
        user = Users.objects.get(pk=user_id)
        instance = serializer.save(user_id=user)

        # Đếm số thông báo chưa đọc
        unread_count = Notifications.objects.filter(user_id=user_id, read_status=False).count()

        # Gửi qua WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_notification",
                "data": {
                    "noti_id": instance.noti_id,
                    "post_id": instance.post_id.post_id,
                    "message": instance.message,
                    "created_at": instance.created_at.isoformat(),
                    "read_status": instance.read_status,
                    "unread_count": unread_count,
                }
            }
        )
    
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
    
class NearbyPostsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Lấy tham số từ URL
            lat = float(request.query_params.get('latitude'))
            lon = float(request.query_params.get('longitude'))
            max_distance = float(request.query_params.get('distance', 2.0))  # Mặc định 2km
            
            # Lấy tất cả bài đăng
            all_posts = Posts.objects.all()
            
            # Lọc các bài đăng trong bán kính
            nearby_posts = []
            for post in all_posts:
                distance = post.distance_to(lat, lon)
                if distance <= max_distance:
                    post.distance = distance  # Thêm khoảng cách vào đối tượng bài đăng
                    nearby_posts.append(post)
            
            # Sắp xếp theo khoảng cách gần nhất
            nearby_posts_sorted = sorted(nearby_posts, key=lambda x: x.distance)
            
            # Serialize dữ liệu
            serializer = PostsSerializer(nearby_posts_sorted, many=True)
            
            # Thêm thông tin khoảng cách vào kết quả
            result_data = []
            for i, post in enumerate(nearby_posts_sorted):
                post_data = serializer.data[i]
                post_data['distance_km'] = round(post.distance, 2)  # Làm tròn đến 2 chữ số
                result_data.append(post_data)
            
            return Response({
                'count': len(result_data),
                'results': result_data
            })
            
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid latitude or longitude values'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )