from django.urls import path

from api.views import post_list_apiview, post_create_apiview, subjob_list_apiview, subjob_detail_apiview, \
    employee_list_apiview, post_detail_apiview, get_my_posts, the_most_popular, the_best_employees, \
    employees_for_subjob, expired_posts, product_create_api_view, order_item_api_view, product_dynamic_fields_api_view, \
    category_detail_api_view, category_create_api_view, order_create_api_view, profile_api_view, \
    products_by_search_api_view, product_activate_api_view, test_order_create_api_view, register_api_view, check_code, \
    forgot_password_api_view, forgot_password_check_api_view, login_api_view, google_login_api_view, \
    facebook_login_api_view

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
    path('expired-posts/', expired_posts),
    path('create-product/', product_create_api_view),
    path('orders/<int:pk>', order_item_api_view),
    path('product/', product_dynamic_fields_api_view),
    path('category/<int:pk>', category_detail_api_view),
    path('category-create/', category_create_api_view),
    path('order-create/', order_create_api_view),
    path('profile/', profile_api_view),
    path('search/', products_by_search_api_view),
    path('products/<int:pk>/activate', product_activate_api_view),
    # path('register/', register_api_view),
    path('test-order/', test_order_create_api_view),
    path('auth/register/', register_api_view),
    path('auth/register/check/', check_code),
    path('auth/forgot_password/', forgot_password_api_view),
    path('auth/forgot_password/check/', forgot_password_check_api_view),
    path('login/', login_api_view),
]
