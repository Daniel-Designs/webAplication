from django.db import models
from django.utils.html import mark_safe
from markdown import markdown
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.text import Truncator
from django.contrib.auth.models import User

#user
class Usuario (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='profile_image', blank=True, default='profile_image/default_profileImage.jpg')
    post_count = models.IntegerField('Post count', blank=True, default=0)
    bio = models.TextField(max_length=2500, null=True,blank=True, default='')
    
    def __str__(self):
        return self.user.username
    
def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = Usuario.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User) 

#forum
class Topic(models.Model):
    name = models.CharField('Subject', max_length=50, unique=True)
    description = models.CharField(max_length=150)
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', null=True)
    user = models.ForeignKey(Usuario, related_name='topicUser',on_delete=models.CASCADE)
    subscribers = models.ManyToManyField(Usuario, blank=True, related_name='topics')
    post_count = models.IntegerField('Post count', blank=True, default=0)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(thread__topic=self).count()
    def get_last_post(self):
        return Post.objects.filter(thread__topic=self).order_by('-updated').first()


class Thread(models.Model):
    name = models.CharField('Name', max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, default='0', related_name='threads')
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE,  related_name='threads')
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)
    body = models.TextField('Message')
    body_html = models.TextField('HTML version')
    post_count = models.IntegerField('Post count', blank=True, default=0)
    no_views = models.IntegerField('Views count', blank=True, default=0)
    
    def __str__(self):
        return self.name
    
    def get_posts_count(self):
        return Post.objects.filter(thread=self).count()

class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=False, default='0', related_name='posts')
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE,  related_name='+', null=True)
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)
    body = models.TextField('Message', max_length=5000)
    body_html = models.TextField('HTML version')
    def __str__(self):
        pm = Truncator(self.body)
        return pm.chars(30)
    def get_body_markdown(self):
        return mark_safe(markdown(self.body, safe_mode='escape'))