from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    path("", views.PhotoListView.as_view(), name="list"),
    path("myphoto/", views.PhotoMyListView.as_view(),
         name="myphoto"),
    path("photos/<int:pk>/detail/", views.PhotoDetailView.as_view(),
          name="detail"),
    path("photos/create/", views.PhotoCreateView.as_view(),
          name="create"),
    path("photos/<int:pk>/edit/", views.PhotoEditView.as_view(),
         name="edit"),
    path("photos/<int:pk>/delete/", views.PhotoDeleteView.as_view(),
         name="delete"),
    path("photo/<int:pk>/comment/", views.CommentCreateView.as_view(),
         name="comment"),
    path("comment/<int:pk>/edit/", views.PhotoCommentEdit.as_view(),
         name="comment_edit"),
    path("comment/<int:pk>/delete/", views.PhotoCommentDelete.as_view(),
         name="comment_delete"),
]