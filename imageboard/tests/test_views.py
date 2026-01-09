import tempfile
import shutil
from io import BytesIO
from pathlib import Path
from PIL import Image

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.conf import settings

from ..models import Photo, PhotoComment

# 一時フォルダをMEDIA_ROOTにする
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PhotoCreateResizeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client.login(username="tester", password="pass1234")

    def tearDown(self):
        # 一時MEDIAディレクトリをクリーンアップ
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        
    def make_test_image(self, size=(2000, 1500), color=(255, 0, 0)):
        """メモリ上にテスト画像を生成"""
        image = Image.new("RGB", size, color)
        buf = BytesIO()
        image.save(buf, format="JPEG")
        return SimpleUploadedFile("test.jpg", buf.getvalue(), content_type="image/jpeg")

    def test_photo_is_resized_and_thumbnail_created(self):
        # 2000x1500 の大きな画像を投稿
        image = self.make_test_image()

        response = self.client.post(reverse("board:create"), {
            "pic": image,
            "message": "テスト投稿"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Photo.objects.count(), 1)

        photo = Photo.objects.first()
        original_path = Path(photo.pic.path)
        thumb_path = Path(photo.thumbnail.path)

        # 画像が保存されている
        self.assertTrue(original_path.exists())
        self.assertTrue(thumb_path.exists())

        # リサイズされたサイズを確認
        with Image.open(original_path) as img:
            self.assertLessEqual(max(img.size), 800)
            self.assertEqual(img.size, (800, 600))
        # サムネイルサイズを確認
        with Image.open(thumb_path) as thumb:
            self.assertLessEqual(max(thumb.size), 300)
            self.assertEqual(thumb.size, (300, 225))
    

class PhotoCommentCreateTests(TestCase):
    def setUp(self):
        # 投稿者
        self.user = User.objects.create_user(username="poster", password="pass1234")
        self.client.login(username="poster", password="pass1234")
        # コメント投稿者
        self.user1 = User.objects.create_user(username="commenter", password="pass5678")

        # 投稿を作成（self.userが投稿者）
        self.photo = Photo.objects.create(
            user=self.user,
            pic=self.make_test_image(),
            message="テスト投稿",
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def make_test_image(self, size=(100, 100), color=(255, 0, 0)):
        """メモリ上にテスト画像を生成"""
        image = Image.new("RGB", size, color)
        buf = BytesIO()
        image.save(buf, format="JPEG")
        return SimpleUploadedFile("test.jpg", buf.getvalue(), content_type="image/jpeg")
    
    def test_create_comment(self):
        
        url = reverse("board:comment", kwargs={"pk": self.photo.pk})
        response = self.client.post(url, {"comment":"コメント投稿テスト"})
        
        self.assertEqual(response.status_code, 302)

        self.assertEqual(PhotoComment.objects.count(), 1)
        comment = PhotoComment.objects.first()
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.photo, self.photo)
        self.assertEqual(comment.comment, "コメント投稿テスト")

    def test_comment_from_other_user(self):
        """別ユーザーがコメントできるか確認"""
        # user1 でログイン
        self.client.login(username="commenter", password="pass5678")

        # コメント投稿
        url = reverse("board:comment", kwargs={"pk": self.photo.pk})
        response = self.client.post(url, {"comment": "他のユーザーからのコメント"})

        # リダイレクト確認
        self.assertEqual(response.status_code, 302)

        # コメントが作成されたか確認
        self.assertEqual(PhotoComment.objects.count(), 1)
        comment = PhotoComment.objects.first()

        # 関連性の確認
        self.assertEqual(comment.user, self.user1)     # コメントしたのは user1
        self.assertEqual(comment.photo, self.photo)     # 対象の投稿に紐づく
        self.assertEqual(comment.comment, "他のユーザーからのコメント")

        print("✅ 別ユーザーによるコメント投稿テスト成功")

    def test_comment_without_login(self):
        url = reverse("board:comment", kwargs={"pk": self.photo.pk})
        self.client.logout()
        response = self.client.post(url, {"comment": "未ログインのユーザーからのコメント"})

        self.assertEqual(response.status_code, 302) # リダイレクト確認
        self.assertIn("/accounts/login/", response.url) 


