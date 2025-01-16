from django.db.models import Count, Sum
from django.db.models.fields import IntegerField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from datetime import datetime

from api.models import Post, SubJob, Employee, User
from api.serializers import PostModelSerializer, SubJobModelSerializer, EmployeeModelSerializer, \
    PostDetailModelSerializer, MyPostModelSerializer, TheMostPopularUserModelSerializer, ExpiredPostModelSerializer


@extend_schema(tags=['post'], responses=PostModelSerializer)
@api_view(['GET'])
def post_list_apiview(request):
    if request.method == 'GET':
        posts = Post.objects.filter(status=Post.PostStatusChoice.NEW)
        s = PostModelSerializer(instance=posts, many=True).data
        return JsonResponse({"response": s}, status=HTTP_200_OK)


@extend_schema(tags=['post'], request=PostModelSerializer)
@api_view(['POST'])
def post_create_apiview(request):
    data = dict(request.POST.items())
    data['file'] = request.FILES.get('file')
    s = PostModelSerializer(data=data)
    if s.is_valid():
        post = s.save()
        serialized_post = PostModelSerializer(instance=post).data
        return JsonResponse({"Post created": serialized_post})
    return JsonResponse({"message": "Something went wrong!"})


@extend_schema(tags=['subjob'], responses=SubJobModelSerializer)
@api_view(['GET'])
def subjob_list_apiview(request):
    subjobs = SubJob.objects.all()
    s = SubJobModelSerializer(instance=subjobs, many=True).data
    return Response(s)


@extend_schema(tags=['subjob'],
               parameters=[
                   OpenApiParameter(
                       name="pk",
                       description=(
                               "Searches for the value in this query parameter returning "
                               "all the users that have this value as substring. Ignores lowercase and uppercase."
                       ),
                       type=str,
                       required=True
                   )
               ],
               responses=SubJobModelSerializer
               )
@api_view(['GET'])
def subjob_detail_apiview(request):
    pk = dict(request.query_params.items()).get('pk')
    if not SubJob.objects.filter(job_id=pk).exists():
        return JsonResponse({"message": f"Subjob with job_id {pk} id not found!"})
    subjobs = SubJob.objects.filter(job_id=pk)
    s = SubJobModelSerializer(instance=subjobs, many=True).data
    return Response(s)


@extend_schema(tags=['employee'], responses=EmployeeModelSerializer)
@api_view(['GET', 'POST'])
def employee_list_apiview(request):
    employees = Employee.objects.all()
    s = EmployeeModelSerializer(instance=employees, many=True).data
    return Response(s, status=HTTP_200_OK)


@extend_schema(tags=['employee'], responses=EmployeeModelSerializer)
@api_view(['GET'])
def employee_detail_apiview(request, pk):
    pass


@extend_schema(tags=['post'], responses=PostDetailModelSerializer)
@api_view(['GET'])
def post_detail_apiview(request, pk):
    if not Post.objects.filter(pk=pk).exists():
        return JsonResponse({"message": f"Post with id {pk} not found!"})
    post = Post.objects.get(pk=pk)
    s = PostDetailModelSerializer(instance=post).data
    return Response(s)


@extend_schema(tags=['homework'], responses=MyPostModelSerializer)
@api_view(['GET'])
def get_my_posts(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "You have to login to see your posts!"})
    posts = Post.objects.filter(user=request.user)
    s = MyPostModelSerializer(instance=posts, many=True).data
    return JsonResponse({'customer_name': request.user.get_full_name(), 'posts': s})


@extend_schema(tags=['homework'], responses=TheMostPopularUserModelSerializer)
@api_view(['GET'])
def the_most_popular(request):
    users = User.objects.annotate(posts_count=Count('posts')).order_by('posts_count')
    fuser = users.first()
    s = TheMostPopularUserModelSerializer(instance=fuser).data
    users = User.objects.annotate(posts_count=Count('posts')).exclude(id=fuser.id).order_by('posts_count')
    my_list = [s]

    for user in users:
        if user.posts_count >= s.get('posts_count'):
            ts = TheMostPopularUserModelSerializer(instance=user).data
            my_list.append(ts)
        else:
            break
    return Response(my_list)


@extend_schema(tags=['homework'], responses=EmployeeModelSerializer)
@api_view(['GET'])
def the_best_employees(request):
    employees = Employee.objects.annotate(
        rating=Sum(Cast('ratings__rating', IntegerField())) / Count('ratings')).order_by('-rating', '-experience')[:5]
    s = EmployeeModelSerializer(instance=employees, many=True).data
    return Response(s)

@extend_schema(tags=['homework'], responses=EmployeeModelSerializer)
@api_view(['GET'])
def employees_for_subjob(request):
    employees = Employee.objects.filter(experience__gte=3)
    s = EmployeeModelSerializer(instance=employees, many=True).data
    return Response(s)

@extend_schema(tags=['homework'], responses=ExpiredPostModelSerializer)
@api_view(['GET'])
def expired_posts(request):
    now = datetime.now()
    posts = Post.objects.filter(deadline__lt=now)
    if not posts.exists():
        return JsonResponse({'message': 'There is not any expired post!'})
    s = ExpiredPostModelSerializer(instance=posts, many=True).data
    return Response(s)
