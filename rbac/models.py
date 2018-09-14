from django.db import models

# Create your models here.

class User(models.Model):
    user = models.CharField(max_length=64)
    pwd = models.CharField(max_length=64)
    roles = models.ManyToManyField("Role")

    def __str__(self):
        return self.user


class Role(models.Model):
    title = models.CharField(max_length=64)
    permissions = models.ManyToManyField("Permission")

    def __str__(self):
        return self.title


class Permission(models.Model):
    url = models.CharField(max_length=124)
    title = models.CharField(max_length=64)
    code = models.CharField(max_length=64)

    def __str__(self):
        return self.title

