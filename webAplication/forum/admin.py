from django.contrib import admin
from .models import Thread, Topic, Usuario, Post

admin.site.register(Topic)
admin.site.register(Thread)
admin.site.register(Usuario)
admin.site.register(Post)


