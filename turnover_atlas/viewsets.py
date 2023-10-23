from django_filters.rest_framework import DjangoFilterBackend
from filters.mixins import FiltersMixin
from rest_framework import viewsets, permissions, renderers, pagination, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from turnover_atlas import pagination as tpagination
from turnover_atlas.models import TurnoverData, TurnoverDataValue, AccessionIDMap, SampleGroupMetadata
from turnover_atlas.serializers import TurnoverDataSerializer, TurnoverDataValueSerializer, AccessionIDMapSerializer, \
    SampleGroupMetadataSerializer
from turnover_atlas.validation import turnover_data_schema, accession_id_map_schema

class TurnoverAtlasDataViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = TurnoverData.objects.all()
    serializer_class = TurnoverDataSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'Protein_Group', 'Genes')
    ordering = ('id',)
    filter_mappings = {
        "Protein_Group": "Protein_Group__exact",
        "Protein_Ids": "Protein_Ids__icontains",
        "Protein_Names": "Protein_Names__exact",
        "Genes": "Genes__icontains",
        "Proteotypic": "Proteotypic__exact",
        "Stripped_Sequence": "Stripped_Sequence__icontains",
        "Modified_Sequence": "Modified_Sequence__icontains",
        "Precursor_Id": "Precursor_Id__icontains",
        "n_Samples": "n_Samples__exact",
        "n_TimePoints": "n_TimePoints__exact",
        "Engine": "Engine__exact",
        "Tissue": "Tissue__exact",
    }
    pagination_class = tpagination.CursorPage
    validation_schema = turnover_data_schema

    def get_queryset(self):
        queryset = TurnoverData.objects.all()
        if self.request.query_params.get('distinct', None):
            queryset = queryset.order_by(self.request.query_params.get('distinct', None)).distinct(self.request.query_params.get('distinct', None))
        return queryset

    @action(detail=True, methods=['get'])
    def values(self, request, pk=None):
        data = self.get_object()
        values = data.values.all()
        json_data = TurnoverDataValueSerializer(values, many=True).data
        return Response(json_data)


class TurnoverAtlasDataValueViewSets(viewsets.ModelViewSet):
    queryset = TurnoverDataValue.objects.all()
    serializer_class = TurnoverDataValueSerializer
    permission_classes = (permissions.AllowAny,)


class AccessionIDMapViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = AccessionIDMap.objects.all()
    serializer_class = AccessionIDMapSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'Protein_Group', 'Genes')
    ordering = ('Protein_Group',)
    filter_mappings = {
        "Protein_Group": "Protein_Group__icontains",
        "Genes": "Genes__icontains",
    }
    validation_schema = accession_id_map_schema

    def get_queryset(self):
        queryset = AccessionIDMap.objects.all()
        if self.request.query_params.get('distinct', None):
            queryset = queryset.order_by(self.request.query_params.get('distinct', None)).distinct(self.request.query_params.get('distinct', None))

        return queryset


class SampleGroupMetadataViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = SampleGroupMetadata.objects.all()
    serializer_class = SampleGroupMetadataSerializer
    permission_classes = (permissions.AllowAny,)


    pagination_class = tpagination.CursorPage
