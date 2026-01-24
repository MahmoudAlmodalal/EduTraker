"""
Pagination utilities for the EduTraker API.

Provides a reusable pagination mixin for APIView classes and standard pagination class.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Standard pagination class with 10 items per page."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaginatedAPIMixin:
    """
    Mixin to add pagination support to APIView classes.
    
    Usage:
        class MyListView(PaginatedAPIMixin, APIView):
            def get(self, request):
                queryset = MyModel.objects.all()
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = MySerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = MySerializer(queryset, many=True)
                return Response(serializer.data)
    """
    pagination_class = StandardPagination
    
    @property
    def paginator(self):
        """Return the paginator instance, creating one if necessary."""
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator
    
    def paginate_queryset(self, queryset):
        """Paginate the queryset if pagination is enabled."""
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    
    def get_paginated_response(self, data):
        """Return a paginated response for the given data."""
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
