"""Proyecto4patas1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from forum import views
#from forum.views import register, profile,editProfile, changePassword
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #general & forum
    path('admin/', admin.site.urls),
    path('home', views.home, name='home'),
    path('', views.home, name='home'),
    path('foro', views.foro, name='foro'),
    path('foro/<str:n>', views.topic_threads, name='topic_threads'),
    path('foro/<str:n>/new_thread', views.new_thread, name='new_thread'),
    path('foro/<str:nTo>/<str:nTh>', views.thread_posts, name='thread_posts'),
    path('foro/<str:nTo>/<str:nTh>/new_post', views.new_post, name='new_post'),
    path('foro/<str:nTo>/<str:nTh>/<int:post_pk>/edit', views.PostUpdateView.as_view(template_name='edit_post.html'), name='edit_post'),
    #users
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name="profile"),
    path('profile/edit', views.editProfile, name='editProfile'),
    path('profile/changePassword', views.changePassword, name='changePassword')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
