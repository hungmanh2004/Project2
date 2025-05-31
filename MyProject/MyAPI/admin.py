from django.contrib import admin
from .models import Users, Posts, Comments, Notifications, PostLike, PostSave

# Register your models here.
admin.site.register(Users)
admin.site.register(Posts)
admin.site.register(Comments)
admin.site.register(Notifications)
admin.site.register(PostLike)
admin.site.register(PostSave)
#     notification_id = models.AutoField(primary_key=True)
