from annoying.decorators import ajax_request
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from .models import InstaUser, Post, Like, Comment, UserConnection
from .forms import CustomUserCreationForm

class HelloWorld(TemplateView):
    template_name = 'test.html'

class PostsView(ListView):
    model = Post
    template_name = 'index.html'

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_authenticated:
            following = set()
            for conn in current_user.get_connections().select_related('following'):
                following.add(conn.following)
            
            return Post.objects.filter(author__in=following)
        return Post.objects.all

class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'

    def get_queryset(self):
        return Post.objects.all().order_by('-posted_on')[:20]

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    fields = ['title', 'image']
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['image', 'title']

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy("posts")

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy("login")

class UserDetailView(LoginRequiredMixin, DetailView):
    model = InstaUser
    template_name = 'user_profile.html'
    login_url = 'login'

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = InstaUser
    template_name='profile_update.html'
    fields = ['profile_pic', 'username', 'email']
    login_url = 'login'

@ajax_request
def addLike(request):
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk=post_pk)
    try:
        like = Like(post=post, user=request.user)
        like.save()
        result = 1
    except Exception as _:
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        result = 0
    
    return {
        'result': result,
        'post_pk': post_pk
    }

@ajax_request
def addComment(request):
    post_pk = request.POST.get('post_pk')
    comment_text = request.POST.get('comment_text')
    post = Post.objects.get(pk=post_pk)
    commenter_info = {}

    try:
        comment = Comment(post=post, user=request.user, comment=comment_text)
        comment.save()
        commenter_info = {
            'username': request.user.username,
            'comment_text': comment_text
        }
        result = 1
    except Exception as e:
        print(e)
        result = 0
    
    return {
        'result': result,
        'post_pk': post_pk,
        'commenter_info': commenter_info
    }

@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk=request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk=follow_user_pk)
    request_type = request.POST.get('type')

    try:
        if current_user != follow_user:
            if request_type == 'follow':
                conn = UserConnection(creator=current_user, following=follow_user)
                conn.save()
            elif request_type =='unfollow':
                conn = UserConnection.objects.get(creator=current_user, following=follow_user)
                conn.delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0
    
    return {
        'result': result,
        'type': request_type,
        'follow_user_pk': follow_user_pk
    }