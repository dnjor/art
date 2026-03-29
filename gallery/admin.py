from django.contrib import admin
from .models import Painting, Comments, Likes


admin.site.register(Painting)
admin.site.register(Comments)
admin.site.register(Likes)