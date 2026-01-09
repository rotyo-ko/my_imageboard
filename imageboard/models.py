from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    pic = models.ImageField(upload_to='photos/', verbose_name="写真")
    thumbnail = models.ImageField(upload_to='thumbnails/',verbose_name="サムネイル")
    message = models.TextField(verbose_name="投稿者コメント", blank=True, default="コメントなし")
    created_at = models.DateTimeField(verbose_name="投稿日時", auto_now_add=True)

class PhotoComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, verbose_name="写真", on_delete=models.CASCADE)
    comment = models.TextField(verbose_name="写真へのコメント",)
    created_at = models.DateTimeField(verbose_name="コメント投稿日時", auto_now_add=True)



