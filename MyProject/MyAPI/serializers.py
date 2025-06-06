from .models import Users, Posts, Comments, Notifications, PostLike, PostSave
from rest_framework import serializers
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class PostsSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField()
    
    class Meta:
        model = Posts
        fields = '__all__'
    
class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = ('post_id',)  # Make post_id read-only
    
    def create(self, validated_data):
        comment = Comments.objects.create(**validated_data)
        
        if comment.receiver_id != comment.sender_id:
            # Tạo notification
            noti = Notifications.objects.create(
                user_id=comment.receiver_id,
                post_id=comment.post_id,
                message=f"{comment.sender_id.username} đã nhắc tới bạn",
                created_at=comment.created_at
            )

            # Gửi notification qua WebSocket
            channel_layer = get_channel_layer()
            unread_count = Notifications.objects.filter(
                user_id=comment.receiver_id, read_status=False
            ).count()

            async_to_sync(channel_layer.group_send)(
                f"user_{comment.receiver_id.user_id}",  # chú ý: dùng .user_id vì là instance User
                {
                    "type": "send_notification",
                    "data": {
                        "noti_id": noti.noti_id,
                        "post_id": noti.post_id.post_id,
                        "message": noti.message,
                        "created_at": noti.created_at.isoformat(),
                        "read_status": noti.read_status,
                        "unread_count": unread_count
                    }
                }
            )
        return comment
    
class PostLikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    post_id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True)
    liked = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    
    def create(self, validated_data):
        post_id = self.context.get('post_id')
        user_id = validated_data.get('user_id')
        
        try:
            post = Posts.objects.get(pk=post_id)
            user = Users.objects.get(pk=user_id)
            
            # Check if like already exists
            like = PostLike.objects.filter(post=post, user=user).first()
            
            if like:
                # Unlike the post
                like.delete()
                # Update like count
                post.like_count = max(0, post.like_count - 1)
                post.save()
                return {
                    'user_id': user_id,
                    'post_id': post_id,
                    'message': 'Post unliked successfully',
                    'liked': False,
                    'like_count': post.like_count
                }
            else:
                # Like the post
                PostLike.objects.create(post=post, user=user)
                # Update like count
                post.like_count += 1
                post.save()
                return {
                    'user_id': user_id,
                    'post_id': post_id,
                    'message': 'Post liked successfully',
                    'liked': True,
                    'like_count': post.like_count
                }
                
        except Posts.DoesNotExist:
            raise serializers.ValidationError('Post not found')
        except Users.DoesNotExist:
            raise serializers.ValidationError('User not found')
    
class PostSaveSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    post_id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True)
    saved = serializers.BooleanField(read_only=True)
    
    def create(self, validated_data):
        post_id = self.context.get('post_id')
        user_id = validated_data.get('user_id')
        
        try:
            post = Posts.objects.get(pk=post_id)
            user = Users.objects.get(pk=user_id)
            
            # Check if save already exists
            save = PostSave.objects.filter(post=post, user=user).first()
            
            if save:
                # Unsave the post
                save.delete()
                return {
                    'user_id': user_id,
                    'post_id': post_id,
                    'message': 'Post unsaved successfully',
                    'saved': False
                }
            else:
                # Save the post
                PostSave.objects.create(post=post, user=user)
                return {
                    'user_id': user_id,
                    'post_id': post_id,
                    'message': 'Post saved successfully',
                    'saved': True
                }
                
        except Posts.DoesNotExist:
            raise serializers.ValidationError('Post not found')
        except Users.DoesNotExist:
            raise serializers.ValidationError('User not found')

class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'
        
    def save(self, *args, **kwargs):
        # Update like count when saving
        if not self.pk:  # Only on create
            self.post.like_count += 1
            self.post.save()
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        # Update like count when deleting
        self.post.like_count -= 1
        self.post.save()
        super().delete(*args, **kwargs)