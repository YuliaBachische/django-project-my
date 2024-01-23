from django.contrib.auth.models import User
from django.db import models


def user_images_directory_path(instance: "Profile", filename: str) -> str:
    return "users/user_{pk}/avatar/{filename}".format(
        pk=instance.user_id,
        filename=filename,
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=user_images_directory_path, null=True, blank=True)
