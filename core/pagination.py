from rest_framework import pagination
from django_filters.rest_framework import DjangoFilterBackend

class CustomPageNumberPagination(pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'p'
