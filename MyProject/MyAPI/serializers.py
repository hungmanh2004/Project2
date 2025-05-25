from .models import Users, Posts, Comments, Notifications
from rest_framework import serializers

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class PostsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Posts
        fields = '__all__'
    
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
    
class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'