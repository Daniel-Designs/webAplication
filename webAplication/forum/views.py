from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, AuthenticationForm
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Thread, Usuario, Post
from .forms import RegistrationForm, EditProfileForm,ProfileForm, NewThreadForm,  NewThreadForm, NewPostForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth import login,authenticate, update_session_auth_hash
from django.utils import timezone
from django.utils.decorators import method_decorator

#forum
def home(request):
    return render(request, 'index.html')

def foro(request):
    queryset =request.GET.get("buscar") 
    #print(queryset)
    topics = Topic.objects.all()
    if queryset:
        topics = Topic.objects.filter(
            Q(name__icontains = queryset) |
            Q(description__icontains = queryset)
        ).distinct()
        
        return render(request, 'foro.html', {'topics': topics})

    else:
        return render(request, 'foro.html', {'topics': topics})
    
def topic_threads(request, n):

    topic = get_object_or_404(Topic, name=n)
    tema =get_object_or_404(Topic, name=n)
    pk = tema.pk
    #print(tema.pk)
    #print(tema.name)
    threads1 =  Thread.objects.filter(topic = pk)
    #for Thread1 in threads1:
     #print(Thread1.name)
    context = {
        'topic' : get_object_or_404(Topic, name=n),
        'threads' : Thread.objects.filter(topic = pk).order_by('-updated'),
    }
    queryset =request.GET.get("buscar")
    #print(queryset)
    if queryset:
        threads1=Thread.objects.filter(
         Q(name__icontains = queryset) &
          Q(topic = pk)
         ).order_by('-updated')
        context = {
        'topic' : get_object_or_404(Topic, name=n),
        'threads' : threads1,
        }
        return render(request, 'threads.html',context)
    else:
        
        return render(request, 'threads.html',context)

@login_required
def new_thread(request, n):
    topic = get_object_or_404(Topic, name=n)
    #user = Usuario.objects.first() #cambiar por usuario logeado
    user = Usuario.objects.get(user=request.user)

    if request.method == 'POST':
        form = NewThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.topic = topic
            thread.user = user
            thread.save()
            '''post = Post.objects.create(
               body=form.cleaned_data.get('body'),
                thread=thread,
                user=thread.user
            )'''
            return redirect('topic_threads', n=topic.name)
    else:
        form = NewThreadForm() 
    return render(request, 'new_thread.html', {'topic': topic, 'form': form})

@login_required
def new_post(request, nTo, nTh):
    thread = get_object_or_404(Thread, topic__name=nTo, name=nTh)
    user = Usuario.objects.get(user=request.user)
    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.user = user
            post.save()

            thread.last_updated = timezone.now()
            thread.save()
            return redirect('thread_posts', nTo=thread.topic.name, nTh=thread.name)
    else:
        form = NewPostForm() 
    return render(request, 'new_post.html', {'thread': thread, 'form': form})

def thread_posts(request, nTo, nTh):
    thread = get_object_or_404(Thread, topic__name=nTo, name=nTh)
    
    session_key = 'viewed_thread_{}'.format(thread.pk)  # <-- here
    if not request.session.get(session_key, False):
        thread.no_views += 1
        thread.save()
        request.session[session_key] = True
    
    thread.save()
    return render(request, 'posts.html', {'thread': thread})

#account
def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('foro')
    else:
        form = RegistrationForm()
    
    args = {'form':form}
    return render(request, 'reg_form.html', args)

def login_view(request,*args, **kwargs):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('foro')
    form = AuthenticationForm()
    return render(request = request,
                    template_name = "login.html",
                    context={"form":form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('body', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=Usuario.objects.get(user=self.request.user))

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = Usuario.objects.get(user=self.request.user)
        post.updated_at = timezone.now()
        post.save()
        return redirect('thread_posts', nTo=post.thread.topic.name, nTh=post.thread.name)

def profile(request, pk=None):
    if pk:
        user = User.objects.get(pk=pk)
    else:
        user = request.user
    args = {'user': user}
    return render(request, 'profile.html', args)

def editProfile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            return redirect('/profile')
    else:
        form = EditProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        args = {}
        args['form'] = form
        args['profile_form'] = profile_form
        return render(request, 'edit_profile.html', args)
    return render(request, 'profile.html', args)

def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('/profile')
        else:
            return redirect('/profile/changePassword')
    else:
        form = PasswordChangeForm(user=request.user)

        args = {'form': form}
        return render(request, 'change_password.html', args)
    return render(request, 'profile.html', args)
