from django.contrib.auth.hashers import make_password
from django.utils.functional import cached_property
from rest_framework.serializers import ValidationError, Serializer
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.fields import CharField, ReadOnlyField, IntegerField, DecimalField, BooleanField, EmailField
from rest_framework.serializers import ModelSerializer
from rest_framework.settings import api_settings
from rest_framework.utils import model_meta
from rest_framework.utils.serializer_helpers import BindingDict
import copy

from api.models import Post, SubJob, Employee, User, Product, Category, OrderItem, Order, TestOrder


class PostModelSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            'jobs': {'required': False}
        }


class SubJobModelSerializer(ModelSerializer):
    class Meta:
        model = SubJob
        fields = '__all__'


class EmployeeModelSerializer(ModelSerializer):
    user_first_name = ReadOnlyField(source='user.first_name')
    user_last_name = ReadOnlyField(source='user.last_name')
    rating = DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Employee
        fields = 'user_first_name', 'user_last_name', 'rating', 'experience', 'linkedin'
        # extra_kwargs = {
        #     "experience": {'write_only': True}
        # }


class PostDetailModelSerializer(ModelSerializer):
    user_first_name = ReadOnlyField(source='user.first_name')
    user_last_name = ReadOnlyField(source='user.last_name')

    class Meta:
        model = Post
        fields = 'title', 'description', 'user_first_name', 'user_last_name'


class MyPostModelSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = 'title', 'status', 'deadline', 'description'


class TheMostPopularUserModelSerializer(ModelSerializer):
    posts_count = IntegerField()

    class Meta:
        model = User
        fields = 'full_name', 'posts_count'


class ExpiredPostModelSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = 'title', 'description', 'deadline'


class ProductModelSerializer(ModelSerializer):
    discount = DecimalField(max_digits=3, decimal_places=0, validators=[MaxValueValidator(100), MinValueValidator(0)],
                            required=False)
    sale = BooleanField(default=False, required=False)

    class Meta:
        model = Product
        fields = 'name', 'price', 'discount', 'sale', 'category'
        extra_kwargs = {
            'category': {'write_only': True}
        }

    def validate_name(self, value):
        if len(value) < 3:
            raise ValidationError("Name is too short!")
        if Product.objects.filter(name=value).exists():
            raise ValidationError("Bu mahsulot nomi allaqachon mavjud!")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise ValidationError("Narx manfiy bo'lishi mumkin emas!")
        return value

    def validate_sale(self, value):
        if value and int(self.root.initial_data.get("discount")) <= 0:
            raise ValidationError("Invalid discount!")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        category = CategoryModelSerializer(instance=instance.category).data
        data['category'] = category
        return data


class CategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self, value):
        if Category.objects.filter(name=value).exists():
            raise ValidationError("Category with this name already exists!")
        if not value.isalpha():
            raise ValidationError("Name must contains only letters!")
        return value


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'full_name',


class OrderItemModelSerializer(ModelSerializer):
    product = ProductModelSerializer()

    class Meta:
        model = OrderItem
        fields = 'product', 'count'


class OrderModelSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def validate(self, attr):
        quantity = attr.get('quantity')
        price = attr.get('amount')
        # product_id = attr.get('product')
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1")
        if price < 10:
            raise ValidationError("Price must be at least 10")
        # if not Product.objects.filter(id=product_id).exists():
        #     raise ValidationError(f"Product with id {product_id} not found1")
        return attr

    def to_representation(self, instance):
        data = super().to_representation(instance)
        items = OrderItem.objects.filter(order=instance).all()
        serialized_user = UserModelSerializer(instance=instance.user).data
        serialized_items = OrderItemModelSerializer(instance=items, many=True).data
        data['user'] = serialized_user
        data['items'] = serialized_items
        return data


class ProductDynamicModelSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # `request` obyektini context orqali olish
        request = self.context.get('request', None)
        if request:
            # Query params orqali fieldlarni olish
            fields = request.query_params.get('fields')
            if fields:
                # Fieldlarni ajratish va filtrlash
                allowed = set(fields.split(','))
                existing = set(self.fields.keys())

                # Ruxsat berilmagan fieldlarni olib tashlash
                for field_name in existing - allowed:
                    self.fields.pop(field_name)


class ProductByCategoryModelSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = 'name', 'price'


class CategoryDetailModelSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        products = Product.objects.filter(category=instance)
        s = ProductByCategoryModelSerializer(instance=products, many=True).data
        data['products'] = s
        return data


class ProfileModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ProductBySearchModelSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# class RegisterModelSerializer(ModelSerializer):
#     class Meta:
#         model = User
#         fields = 'email', 'password', 'is_active',
#         extra_kwargs = {
#             'password': {'write_only': True},
#             'is_active': {'read_only': True}
#         }
#
#     def validate_username(self, value):
#         if User.objects.filter(username=value).exists():
#             raise ValidationError("User with this username already registered!")
#         return value
#
#     def validate_password(self, value):
#         return make_password(value)


class TestOrderModelSerializer(ModelSerializer):
    class Meta:
        model = TestOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

        # extra_kwargs = {
        #     'phone_number': {'required': False},
        #     'longitude': {'required': False},
        #     'latitude': {'required': False},
        # }

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        is_status = attrs.get('is_status')
        longitude = attrs.get('longitude')
        latitude = attrs.get('latitude')

        if is_status:
            if not phone_number:
                raise ValidationError("Telefon raqam majburiy!")
            if not longitude or not latitude:
                raise ValidationError("Location majburiy!")

        return attrs


# class RegisterSerializer(Serializer):
#     first_name = CharField(max_length=128)
#     last_name = CharField(max_length=128)
#     email = EmailField()
#
#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise ValidationError("This email already registered!")
#         return value


class RegisterModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email'
