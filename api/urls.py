from django.urls import path

from api.views import post_list_apiview, post_create_apiview, subjob_list_apiview, subjob_detail_apiview, \
    employee_list_apiview, post_detail_apiview, get_my_posts, the_most_popular, the_best_employees, \
    employees_for_subjob, expired_posts

urlpatterns = [
    path('post', post_list_apiview),
    path('post-create/', post_create_apiview),
    path('subjob/', subjob_list_apiview),
    path('subjob-detail', subjob_detail_apiview),
    path('employee/', employee_list_apiview),
    path('employee/<int:pk>', employee_list_apiview),
    path('post/<int:pk>', post_detail_apiview),
    path('my-posts/', get_my_posts),
    path('popular-user/', the_most_popular),
    path('the-best/', the_best_employees),
    path('employee-front-end/', employees_for_subjob),
    path('expired-posts/', expired_posts)
]