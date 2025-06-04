from .models import Users, Posts, Comments, Notifications, PostLike, PostSave
from rest_framework import serializers

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class PostsSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Posts
        fields = '__all__'
        read_only_fields = ('like_count',)
    
class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = ('post_id',)  # Make post_id read-only
    
    def create(self, validated_data):
        # Create the comment
        comment = Comments.objects.create(**validated_data)
        
        # Create notification if receiver is different from sender
        if comment.receiver_id != comment.sender_id:
            Notifications.objects.create(
                user_id=comment.receiver_id,
                post_id=comment.post_id,
                message=f"{comment.sender_id.username} đã nhắc tới bạn",
                created_at=comment.created_at
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
        
    def save(self, **kwargs):
        # Kiểm tra xem đây có phải là tạo mới hay không
        if self.instance is None:  # Nếu là tạo mới
            # Gọi save bình thường
            instance = super().save(**kwargs)
            # Nếu có post_id và muốn tăng like_count
            if hasattr(instance, 'post_id') and instance.post_id:
                try:
                    post = instance.post_id
                    if hasattr(post, 'like_count'):
                        post.like_count += 1
                        post.save(update_fields=['like_count'])
                except Exception:
                    pass
            return instance
        # Nếu là cập nhật, gọi save bình thường
        return super().save(**kwargs)
        
    def delete(self, instance):
        # Xử lý khi xóa notification
        if hasattr(instance, 'post_id') and instance.post_id:
            try:
                post = instance.post_id
                if hasattr(post, 'like_count'):
                    post.like_count = max(0, post.like_count - 1)
                    post.save(update_fields=['like_count'])
            except Exception:
                pass
        instance.delete()