from rest_framework.fields import CharField, ReadOnlyField, IntegerField, DecimalField
from rest_framework.serializers import ModelSerializer

from api.models import Post, SubJob, Employee, User


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