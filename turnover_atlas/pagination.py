from rest_framework import pagination

class CursorPage(pagination.CursorPagination):
    page_size = 20
    ordering = '-id'
    cyrsor_query_param = 'cursor'

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('page_size'):

            self.page_size = int(request.query_params.get('page_size'))
            if self.page_size == 0:
                return None
        print(self.page_size)
        print(request.query_params.get('page_size'))
        print(queryset)
        return super().paginate_queryset(queryset, request, view=view)