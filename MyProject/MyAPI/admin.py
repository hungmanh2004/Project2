from django.contrib import admin
from .models import Users, Posts, Comments, Notifications

# Register your models here.
admin.site.register(Users)
admin.site.register(Posts)
admin.site.register(Comments)
admin.site.register(Notifications)
#     notification_id = models.AutoField(primary_key=True)
