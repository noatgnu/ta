import numpy as np
import pandas as pd
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from filters.mixins import FiltersMixin
from rest_framework import viewsets, permissions, renderers, pagination, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from turnover_atlas import pagination as tpagination
from turnover_atlas.models import TurnoverData, TurnoverDataValue, AccessionIDMap, SampleGroupMetadata, ModelParameters
from turnover_atlas.ordering_filter import CustomOrderingFilter
from turnover_atlas.serializers import TurnoverDataSerializer, TurnoverDataValueSerializer, AccessionIDMapSerializer, \
    SampleGroupMetadataSerializer, ModelParametersSerializer
from turnover_atlas.utils import func_kpool, func_pulse
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

    @method_decorator(cache_page(60 * 60 * 24 * 7))
    @action(detail=False, methods=['get'])
    def get_all_from_queryset(self, request, pk=None):
        queryset = self.get_queryset()
        json_data = TurnoverDataSerializer(queryset, many=True).data
        return Response(json_data)

    @action(detail=True, methods=['get'])
    def values(self, request, pk=None):
        data = self.get_object()
        values = data.values.all()
        json_data = TurnoverDataValueSerializer(values, many=True).data
        return Response(json_data)

    @action(detail=False, methods=['post'])
    def get_modelling_data(self, request, pk=None):
        filter_ids = self.request.data["ids"]
        turnover_data = TurnoverData.objects.filter(tau_POI__isnull=False, id__in=filter_ids)
        results = []
        for i in turnover_data:
            engine = i.Engine
            tissue = i.Tissue
            tau_POI = i.tau_POI
            days = self.request.data["Data"]
            params = ModelParameters.objects.filter(Engine=engine, Tissue=tissue).first()
            # calculate kpool for 5-minutes interval from 0 to 50 days where the unit is days and return a json arrays of kpool value and day value
            if params is not None:
                pulse = []
                available_days = []
                for i2 in i.values.all():
                    if i2.Sample_H_over_HL is not None:
                        s = SampleGroupMetadata.objects.get(Sample_Name=i2.Sample_Name)
                        if s.Days not in available_days and s.Days in days:
                            available_days.append(s.Days)
                if 0 not in available_days:
                    available_days.append(0)
                if 50 not in available_days:
                    available_days.append(50)
                available_days.sort()
                for d in available_days:
                    day = d
                    value = func_pulse(d, params.a, params.b, params.r, tau_POI)
                    data = {"value": value, "day": day}
                    pulse.append(data)
                results.append({"Data": pulse, "Tissue": tissue, "Engine": engine, "Precursor_Id": i.Precursor_Id})

        return Response(results)

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

    @action(detail=False, methods=['get'])
    def get_distinct(self, request, pk=None):
        queryset = self.get_queryset()
        result = queryset.values_list(self.request.query_params.get('distinct', None), flat=True).distinct()
        count_result = result.count()
        if count_result < 10:
            return Response(result)
        return Response(result[:10])


class SampleGroupMetadataViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = SampleGroupMetadata.objects.all()
    serializer_class = SampleGroupMetadataSerializer
    permission_classes = (permissions.AllowAny,)


    pagination_class = tpagination.CursorPage


class ModelParametersViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = ModelParameters.objects.all()
    serializer_class = ModelParametersSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'Engine', 'Tissue')
    ordering = ('id',)
    filter_mappings = {
        "Engine": "Engine__exact",
        "Tissue": "Tissue__exact",
    }