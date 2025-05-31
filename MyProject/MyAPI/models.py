from django.db import models
from math import radians, sin, cos, sqrt, atan2

# Create your models here.
class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100, blank=False)
    phone = models.CharField(max_length=20, blank=False)
    password = models.CharField(max_length=255, blank=False)
    role = models.BooleanField(default=False)
    
    def __str__(self):
        return "(" + str(self.user_id) + ")" + self.username
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['user_id']
        indexes = [
            models.Index(fields=['user_id']),
        ]
    
class Posts(models.Model):
    post_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    species = models.CharField(max_length=255)
    breed = models.CharField(max_length=255)
    status = models.BooleanField(default=False)
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    post_time = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return "(" + str(self.post_id) + ")" + self.description
    
    def distance_to(self, lat, lon):
        # Bán kính trái đất tính bằng km
        R = 6371.0
        
        # Chuyển đổi độ sang radian
        lat1 = radians(self.latitude)
        lon1 = radians(self.longitude)
        lat2 = radians(lat)
        lon2 = radians(lon)
        
        # Tính toán chênh lệch
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Công thức Haversine
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return distance
    
    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['post_time']
        indexes = [
            models.Index(fields=['post_id']),
        ]
    
class Comments(models.Model):
    cmt_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE)
    sender_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sender')
    receiver_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='receiver')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['cmt_id']),
        ]

class Notifications(models.Model):
    noti_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Posts, on_delete=models.CASCADE)
    message = models.TextField()
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['created_at']

class PostLike(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "Post Like"
        verbose_name_plural = "Post Likes"
        
class PostSave(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='saves')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "Post Save"
        verbose_name_plural = "Post Saves"