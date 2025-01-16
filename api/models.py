from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model, TextField, FileField, DateTimeField, BooleanField, CharField, ForeignKey, CASCADE, \
    ManyToManyField, DecimalField, PositiveSmallIntegerField, Sum, Count
from django.db.models.enums import TextChoices


class User(AbstractUser):
    phone_number = CharField(max_length=128)

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.first_name}"


class Post(Model):
    class PostStatusChoice(TextChoices):
        NEW = 'new', "New"
        COMPLETED = 'completed', 'Completed'

    title = CharField(max_length=128)
    description = TextField()
    file = FileField(upload_to='posts/')
    deadline = DateTimeField()
    status = CharField(max_length=55, choices=PostStatusChoice.choices, default=PostStatusChoice.NEW)
    user = ForeignKey(User, on_delete=CASCADE, related_name='posts')
    jobs = ManyToManyField('Job', related_name='posts')


class Job(Model):
    name = CharField(max_length=255)


class SubJob(Model):
    job = ForeignKey(Job, on_delete=CASCADE, related_name='subs')
    name = CharField(max_length=128)


class Employee(Model):
    experience = PositiveSmallIntegerField(default=0)
    linkedin = TextField()
    description = TextField()
    user = ForeignKey(User, on_delete=CASCADE, related_name='employees')
    cv = FileField(upload_to='user_cv/')



class Rating(Model):
    class RatingChoice(TextChoices):
        one = '1', '1'
        two = '2', '2'
        three = '3', '3'
        four = '4', '4'
        five = '5', '5'

    employee = ForeignKey(Employee, on_delete=CASCADE, related_name='ratings')
    rating = CharField(max_length=1, choices=RatingChoice.choices)
