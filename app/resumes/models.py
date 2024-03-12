from django.db.models import JSONField
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField("users.User", related_name="profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    phone = models.CharField(blank=True, max_length=17)
    email = models.EmailField()
    linkedin_username = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Education(models.Model):
    user = models.ForeignKey("users.User", related_name='educations', on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    course = models.CharField(max_length=200, blank=True, null=True)
    duration = models.CharField(max_length=100)


class Experience(models.Model):
    user = models.ForeignKey("users.User", related_name='experiences', on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=100)
    description = JSONField(default=list, blank=True, null=True)


class Project(models.Model):
    user = models.ForeignKey("users.User", related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    description = JSONField(default=list, blank=True, null=True)


class Achievement(models.Model):
    user = models.ForeignKey("users.User", related_name='achievements', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = JSONField(default=list, blank=True, null=True)


class Skill(models.Model):
    user = models.ForeignKey("users.User", related_name='skills', on_delete=models.CASCADE)
    skill = models.CharField(max_length=100)  # For example: Languages, Tools, Libraries
    value = models.TextField()  # Comma-separated values or similar


class ProfileLink(models.Model):
    user = models.OneToOneField("users.User", related_name="profile_links", on_delete=models.CASCADE)
    platform = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
