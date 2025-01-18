from django.db.models import Count, Sum, Q
from django.db.models.fields import IntegerField, FloatField
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED
from datetime import datetime

from api.models import Post, SubJob, Employee, User, Category, Order, Product
from api.serializers import PostModelSerializer, SubJobModelSerializer, EmployeeModelSerializer, \
    PostDetailModelSerializer, MyPostModelSerializer, TheMostPopularUserModelSerializer, ExpiredPostModelSerializer, \
    ProductModelSerializer, CategoryModelSerializer, OrderModelSerializer, ProductDynamicModelSerializer, \
    CategoryDetailModelSerializer, ProfileModelSerializer, ProductByCategoryModelSerializer, \
    ProductBySearchModelSerializer, RegisterModelSerializer


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
    return Response(s, status=HTTP_200_OK)


@extend_schema(tags=['homework-2'], responses=MyPostModelSerializer)
@api_view(['GET'])
def get_my_posts(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "You have to login to see your posts!"})
    posts = Post.objects.filter(user=request.user)
    s = MyPostModelSerializer(instance=posts, many=True).data
    return JsonResponse({'customer_name': request.user.get_full_name(), 'posts': s}, status=HTTP_200_OK)


@extend_schema(tags=['homework-2'], responses=TheMostPopularUserModelSerializer)
@api_view(['GET'])
def the_most_popular(request):
    users = User.objects.annotate(posts_count=Count('posts')).order_by('-posts_count')
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
    return Response(my_list, status=HTTP_200_OK)


@extend_schema(tags=['homework-2'], responses=EmployeeModelSerializer)
@api_view(['GET'])
def the_best_employees(request):
    employees = Employee.objects.annotate(
        rating=Sum(Cast('ratings__rating', FloatField())) / Count('ratings')).order_by('-rating', '-experience')[:5]
    s = EmployeeModelSerializer(instance=employees, many=True).data
    return Response(s, status=HTTP_200_OK)


@extend_schema(tags=['homework-2'], responses=EmployeeModelSerializer)
@api_view(['GET'])
def employees_for_subjob(request):
    employees = Employee.objects.filter(experience__gte=3)
    s = EmployeeModelSerializer(instance=employees, many=True).data
    return JsonResponse({"Subjob name": "Front end", "employees": s}, status=HTTP_200_OK)


@extend_schema(tags=['homework-2'], responses=ExpiredPostModelSerializer)
@api_view(['GET'])
def expired_posts(request):
    now = datetime.now()
    posts = Post.objects.filter(deadline__lt=now)
    if not posts.exists():
        return JsonResponse({'message': 'There is not any expired post!'})
    s = ExpiredPostModelSerializer(instance=posts, many=True).data
    return Response(s, status=HTTP_200_OK)


@extend_schema(tags=['homework-3'], responses=ProductModelSerializer, request=ProductModelSerializer)
@api_view(['POST'])
def product_create_api_view(request):
    data = request.data
    s = ProductModelSerializer(data=data)
    if s.is_valid():
        product = s.save()
        serialized_product = ProductModelSerializer(instance=product).data
        return JsonResponse({"Product created": serialized_product}, status=HTTP_201_CREATED)

    return JsonResponse(s.errors)


@extend_schema(tags=['Order'], responses=OrderModelSerializer)
@api_view(['GET'])
def order_item_api_view(request, pk):
    if not Order.objects.filter(id=pk).exists():
        return JsonResponse({"message": f"Order with id {pk} not found!"})
    order = Order.objects.get(id=pk)
    serialized_order = OrderModelSerializer(instance=order).data
    return JsonResponse(serialized_order, status=HTTP_200_OK)
    # try:
    #     order = Order.objects.get(id=pk)
    #     serialized_order = OrderModelSerializer(instance=order).data
    #     return JsonResponse(serialized_order)
    # except:
    #     return JsonResponse({"message": f"Order with id {pk} not found!"})


@extend_schema(tags=['Product'], responses=ProductModelSerializer, parameters=[
    OpenApiParameter(
        name="fields",
        description=(
                "Ro'yxat qiymat qabul qiladi. Masalan: ?fields=name,price"
        ),
        type={
            "type": "array",
            "items": {"type": "string"}
        },
        explode=False,
        style="form",  # Query param uchun mos format
        required=True  # Ixtiyoriy
    )
])
@api_view(['GET'])
def product_dynamic_fields_api_view(request):
    fields = request.query_params.get('fields').split(',')
    products = Product.objects.all()
    s = ProductDynamicModelSerializer(instance=products, many=True).data
    return Response(s)


@extend_schema(tags=['homework-3'], responses=CategoryDetailModelSerializer)
@api_view(['GET'])
def category_detail_api_view(request, pk):
    if not Category.objects.filter(id=pk).exists():
        return JsonResponse({"message": f"Category with id {pk} not found!"})
    category = Category.objects.get(id=pk)
    s = CategoryDetailModelSerializer(instance=category).data
    return Response(s, status=HTTP_200_OK)


@extend_schema(tags=['homework-3'], responses=CategoryModelSerializer, request=CategoryModelSerializer)
@api_view(['POST'])
def category_create_api_view(request):
    data = request.data
    s = CategoryModelSerializer(data=data)
    if s.is_valid():
        category = s.save()
        serialized_category = CategoryModelSerializer(instance=category).data
        return JsonResponse(serialized_category, status=HTTP_201_CREATED)
    return JsonResponse(s.errors)


@extend_schema(tags=['homework-3'], responses=OrderModelSerializer, request=OrderModelSerializer)
@api_view(['POST'])
def order_create_api_view(request):
    data = request.data
    s = OrderModelSerializer(data=data)
    if s.is_valid():
        order = s.save()
        serialized_order = OrderModelSerializer(instance=order).data
        return JsonResponse(serialized_order, status=HTTP_201_CREATED)
    return JsonResponse(s.errors)


@extend_schema(tags=['homework-3'])
@api_view(['POST'])
def profile_api_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "You need to login in!"})
    s = ProfileModelSerializer(instance=request.user).data
    if not request.user.is_superuser:
        allowed_fields = ['username', 'email']
        keys_to_remove = []
        for key in s.keys():
            if key not in allowed_fields:
                keys_to_remove.append(key)
        for k in keys_to_remove:
            s.pop(k)
    return JsonResponse(s)


@extend_schema(tags=['homework-3'], responses=ProductByCategoryModelSerializer, parameters=[
    OpenApiParameter(
        name="search",
        description=(
                "..."
        ),
        type={
            "type": "string",
        },
        explode=False,
        style="form",
        required=True
    )
])
@api_view(['GET'])
def products_by_search_api_view(request):
    search = request.query_params.get('search', None)
    if search:
        products = Product.objects.filter(Q(name__icontains=search) | Q(description__icontains=search))
        s = ProductBySearchModelSerializer(instance=products, many=True).data
        return Response(s, status=HTTP_200_OK)
    return JsonResponse({"message": "Please send request with serach!"})


@extend_schema(tags=['homework-3'])
@api_view(['GET'])
def product_activate_api_view(request, pk):
    product = Product.objects.filter(id=pk)
    if not product.exists():
        return JsonResponse({"message": f"Product with id {pk} not found!"})
    if product.first().is_active:
        return JsonResponse({"message": "is_active is already True"})
    product.update(is_active=True)
    return JsonResponse({"message": "Updated!"}, status=HTTP_202_ACCEPTED)


@extend_schema(tags=['homework-3'], responses=RegisterModelSerializer, request=RegisterModelSerializer)
@api_view(['POST'])
def register_api_view(request):
    data = request.data
    s = RegisterModelSerializer(data=data)
    if s.is_valid():
        user = s.save()
        serialized_user = RegisterModelSerializer(instance=user).data
        return JsonResponse(serialized_user, status=HTTP_201_CREATED)
    return JsonResponse(s.errors)
