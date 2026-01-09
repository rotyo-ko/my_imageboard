from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse

from PIL import Image
from pathlib import Path
from django.conf import settings
from .models import Photo, PhotoComment
from .forms import PhotoCommentForm


class PhotoListView(ListView):
    model = Photo
    template_name = "board.html"
    paginate_by = 15


class PhotoMyListView(LoginRequiredMixin, ListView):
    model = Photo
    template_name = "myphoto.html"
    paginate_by = 15
    def get_queryset(self):
        photos = Photo.objects.filter(user=self.request.user)
        return photos
    

class PhotoDetailView(DetailView):
    model = Photo
    template_name = "detail.html"
    context_object_name = "photo"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = PhotoComment.objects.filter(photo=self.object)
        context["comments"] = comments
        context["form"] = PhotoCommentForm()
        return context
        
        
class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    template_name = "post_form.html"
    fields = ["pic", "message"]      # model=Photoからfieldsを指定してformを作る
    success_url = reverse_lazy("board:list")
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        photo = self.object
        img_path = Path(photo.pic.path)
        img = Image.open(img_path)

        max_size = 800
        if img.width > img.height: 
            if img.width > max_size:
                ratio = img.height / img.width
                new_size = (max_size, int(max_size * ratio))
                img = img.resize(new_size)
                img.save(img_path, quality=85)
        else:
            if img.height > max_size:
                ratio = img.width / img.height 
                new_size = (int(max_size * ratio), max_size)
                img = img.resize(new_size)
                img.save(img_path, quality=85)
        thumb_size = (300, 300)
        img.thumbnail(thumb_size)
        thumb_dir = Path(settings.MEDIA_ROOT) / "thumbnails"
        thumb_dir.mkdir(parents=True, exist_ok=True)

        thumb_name = f"thumb_{img_path.name}" # os.path.basename(img_path)
        thumb_path = thumb_dir / thumb_name
        
        img.save(thumb_path, quality=85)
        photo.thumbnail.name = f"thumbnails/{thumb_name}"
        photo.save()

        return response



class PhotoEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Photo
    template_name = "post_form.html"
    fields = ["message"]
    success_url = reverse_lazy("board:list")
    
    def test_func(self):
        photo = self.get_object()
        return photo.user == self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        photo = self.object
        if not photo.message.strip().startswith("(修正済み)"):
            photo.message = "(修正済み)" + photo.message
        photo.save()
        
        return response

    
class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Photo
    template_name = "delete_confirm.html"
    success_url = reverse_lazy("board:list")
    def test_func(self):
        photo = self.get_object()
        return photo.user == self.request.user
    

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = PhotoComment
    template_name = "detail.html"
    fields = ["comment"]
    def form_valid(self, form):
        form.instance.user = self.request.user
        photo = get_object_or_404(Photo, pk=self.kwargs["pk"])
        form.instance.photo = photo
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse("board:detail", kwargs={"pk":self.kwargs["pk"]})

class PhotoCommentEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PhotoComment
    template_name = "comment_edit.html"
    fields = ["comment"]
    
    def test_func(self):
        comment = self.get_object()
        return comment.user == self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        comment = self.object
        if not comment.comment.strip().startswith("(修正済み)"):
            comment.comment = "(修正済み)" + comment.comment
        comment.save()
        return response
    
    def get_success_url(self):
        comment = self.get_object()
        return reverse("board:detail", kwargs={"pk": comment.photo.pk})
    
class PhotoCommentDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PhotoComment
    template_name = "delete_confirm.html"
    
    def test_func(self):
        comment = self.get_object()
        return comment.user == self.request.user
    
    def get_success_url(self):
        comment = self.get_object()
        return reverse("board:detail", kwargs={"pk": comment.photo.pk})






