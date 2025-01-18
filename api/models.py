from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Model, TextField, FileField, DateTimeField, BooleanField, CharField, ForeignKey, CASCADE, \
    ManyToManyField, DecimalField, PositiveSmallIntegerField, Sum, Count, ImageField, SET_NULL
from django.db.models.enums import TextChoices
from django.db.models.fields import PositiveIntegerField, IntegerField


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


class Category(Model):
    name = CharField(max_length=255)

class Product(Model):
    name = CharField(max_length=128)
    discount = DecimalField(max_digits=3, decimal_places=0, validators=[MaxValueValidator(100), MinValueValidator(0)], null=True, blank=True)
    price = PositiveIntegerField()
    sale = BooleanField(default=False, null=True, blank=True)
    description = TextField(null=True, blank=True)
    photo = ImageField(upload_to='products/', null=True, blank=True)
    category = ForeignKey(Category, on_delete=CASCADE, related_name='products')
    is_active = BooleanField(default=True)

class Order(Model):
    class OrderStatusChoice(TextChoices):
        in_process = 'in process', 'In process'
        delivering = 'delivering', 'Delivering'
        delivered = 'delivered', 'Delivered'
        canceled = 'canceled', 'Canceled'
    user = ForeignKey(User, on_delete=SET_NULL, related_name='orders', null=True, blank=True)
    phone_number = CharField(max_length=128)
    longitude = DecimalField(max_digits=10, decimal_places=6)
    latitude = DecimalField(max_digits=10, decimal_places=6)
    status = CharField(max_length=128)
    quantity = PositiveSmallIntegerField(default=1)
    amount = IntegerField()
    product = ForeignKey(Product, on_delete=SET_NULL, related_name='orders', null=True, blank=True)


class OrderItem(Model):
    count = PositiveSmallIntegerField(default=1)
    product = ForeignKey(Product, on_delete=SET_NULL, related_name='order_items', null=True, blank=True)
    order = ForeignKey(Order, on_delete=CASCADE, related_name='order_items')

