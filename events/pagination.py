from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100


class WebPagination(PageNumberPagination):
    page_size = 10


class MobilePagination(PageNumberPagination):
    page_size = 10


def get_paginator_class(request):
    page_size = request.query_params.get("page_size")
    if page_size:
        CustomPagination.page_size = int(page_size)
        return CustomPagination
    user_agent = request.headers.get("Type", "").lower()
    if (
        "mobile" in user_agent
        or "android" in user_agent
        or "ios" in user_agent
    ):
        return MobilePagination
    return WebPagination