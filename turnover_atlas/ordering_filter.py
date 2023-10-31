from rest_framework import filters

class CustomOrderingFilter(filters.OrderingFilter):
    def get_ordering(self, request, queryset, view):
        # filter by column name in the distinct parameter
        distinct = request.query_params.get('distinct', None)
        if distinct:
            return distinct
        ordering = super(CustomOrderingFilter, self).get_ordering(request, queryset, view)
        if ordering:
            return ordering
