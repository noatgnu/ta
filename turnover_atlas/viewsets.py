import numpy as np
import pandas as pd
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django_filters.rest_framework import DjangoFilterBackend
from filters.mixins import FiltersMixin
from rest_framework import viewsets, permissions, renderers, pagination, filters, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from turnover_atlas import pagination as tpagination
from turnover_atlas.models import TurnoverData, TurnoverDataValue, AccessionIDMap, SampleGroupMetadata, ModelParameters, \
    ProteinSequence, Session
from turnover_atlas.ordering_filter import CustomOrderingFilter
from turnover_atlas.serializers import TurnoverDataSerializer, TurnoverDataValueSerializer, AccessionIDMapSerializer, \
    SampleGroupMetadataSerializer, ModelParametersSerializer, ProteinSequenceSerializer, SessionSerializer
from turnover_atlas.utils import func_kpool, func_pulse
from turnover_atlas.validation import turnover_data_schema, accession_id_map_schema

class TurnoverAtlasDataViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = TurnoverData.objects.all()
    serializer_class = TurnoverDataSerializer
    permission_classes = (permissions.IsAuthenticated,)
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
        tau_POI_valid = self.request.query_params.get("valid_tau", "True")
        if tau_POI_valid == "True":
            turnover_data = TurnoverData.objects.filter(tau_POI__isnull=False, id__in=filter_ids)
        else:
            turnover_data = TurnoverData.objects.filter(id__in=filter_ids)
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

    @method_decorator(cache_page(60 * 60 * 24 * 7))
    @action(detail=False, methods=['get'])
    def get_stats(self, request, pk=None):
        include_shared = self.request.query_params.get('include_shared', "False")
        groupby = self.request.query_params.get('groupby', "Tissue,Engine")
        valid_tau = self.request.query_params.get("valid_tau", "True")
        distinct = self.request.query_params.get('distinct', None)
        groupby = groupby.split(",")
        data = TurnoverData.objects.all()

        if include_shared == "False":
            data = data.filter(~Q(Protein_Ids__contains=";"))
        if valid_tau == "True":
            data = data.filter(tau_POI__isnull=False)
        if distinct is not None:
            group = groupby+[distinct]
            turnover_data = data.values(*group).order_by(distinct).distinct(distinct)
            df = pd.DataFrame([i for i in turnover_data])
            rename = {}
            rename[distinct] = "n"
            turnover_data = df.groupby(groupby).count().reset_index().rename(columns=rename).to_dict(orient="records")
            return Response(turnover_data)

        else:
            turnover_data = data.values(*groupby).annotate(n=Count('pk')).order_by(*groupby)

            return Response([i for i in turnover_data])

    @method_decorator(cache_page(60 * 60 * 24 * 7))
    @action(detail=False, methods=['get'])
    def get_histogram(self, request, pk=None):
        include_shared = self.request.query_params.get('include_shared', "False")

        data = TurnoverData.objects.all().filter(tau_POI__isnull=False)
        if include_shared == "False":
            data = data.filter(~Q(Protein_Ids__contains=";"))
        data = data.values("Tissue", "Engine", "tau_POI")
        df = pd.DataFrame(data)
        results = []
        df["tau_POI"] = np.log2(df["tau_POI"])
        result = np.histogram(df["tau_POI"],30)
        data = {"Tissue": "all", "Engine": "all", "value": list(result[0]), "bins": list(result[1])}
        results.append(data)
        for i, d in df.groupby(["Tissue", "Engine"]):
            result = np.histogram(d["tau_POI"],30)
            data = {"Tissue": i[0], "Engine": i[1], "value": list(result[0]), "bins": list(result[1])}
            results.append(data)
        return Response(results)

    @action(methods=['get'], detail=False)
    def get_summary(self, request, pk=None):
        Protein_Group = self.request.query_params.get("Protein_Group", None)
        if Protein_Group == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = TurnoverData.objects.filter(Protein_Group__exact=Protein_Group).values("Tissue", "Engine", "AverageRSS", "HalfLife_POI")
        df = pd.DataFrame(data)
        result = []
        for i, g in df.groupby(["Tissue", "Engine"]):
            x = g[pd.notnull(g["HalfLife_POI"])]
            averagerss_med = x["AverageRSS"].median()
            averagerss_sd = x["AverageRSS"].std()
            halflife_poi_med = x["HalfLife_POI"].median()
            halflife_poi_sd = x["HalfLife_POI"].std()
            valid_peptide = x.shape[0]
            if pd.notnull(halflife_poi_med):
                result.append({"Tissue": i[0], "Engine": i[1], "AvgRSSMedian": round(averagerss_med, 4), "HLMedian": round(halflife_poi_med, 4), "AvgRSSsd": round(averagerss_sd, 4), "HLsd": round(halflife_poi_sd, 4), "Peptides": valid_peptide, "AllPeptides": g.shape[0]})
        df2 = pd.DataFrame(result)
        df3 = df2.set_index(["Tissue", "Engine"]).unstack()
        # flatten column index
        df3.columns = ["_".join(i) for i in df3.columns]
        df3.reset_index(inplace=True)
        return Response(df3.to_dict(orient="records"))

class TurnoverAtlasDataValueViewSets(viewsets.ModelViewSet):
    queryset = TurnoverDataValue.objects.all()
    serializer_class = TurnoverDataValueSerializer
    permission_classes = (permissions.IsAuthenticated,)


class AccessionIDMapViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = AccessionIDMap.objects.all()
    serializer_class = AccessionIDMapSerializer
    permission_classes = (permissions.IsAuthenticated,)
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
    def get_exact_accession_id_from_genes(self, request, pk=None):
        genes = self.request.query_params.get('genes', None)
        if genes is not None:
            queryset = self.get_queryset()
            result = queryset.filter(Genes__exact=genes).values_list('Protein_Group', flat=True).distinct()
            return Response(result)
        return Response(status=status.HTTP_404_NOT_FOUND)

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
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = tpagination.CursorPage


class ModelParametersViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = ModelParameters.objects.all()
    serializer_class = ModelParametersSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'Engine', 'Tissue')
    ordering = ('id',)
    filter_mappings = {
        "Engine": "Engine__exact",
        "Tissue": "Tissue__exact",
    }


class ProteinSequenceViewSets(FiltersMixin, viewsets.ModelViewSet):
    queryset = ProteinSequence.objects.all()
    serializer_class = ProteinSequenceSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id', 'AccessionID')
    ordering = ('AccessionID',)
    filter_mappings = {
        "AccessionID": "AccessionID__exact",
    }

    def get_queryset(self):
        return ProteinSequence.objects.all()

    #@method_decorator(cache_page(60 * 60*24*7))
    @action(detail=False, methods=['get'])
    #@method_decorator(cache_page(60 * 60 * 24 * 7))
    def get_coverage(self, request, pk=None):
        valid_tau = self.request.query_params.get('valid_tau', "True")

        protein_sequence = ProteinSequence.objects.get(AccessionID=self.request.query_params.get('AccessionID', None))
        if protein_sequence is not None:
            if valid_tau == "True":
                turnover_data = TurnoverData.objects.filter(Protein_Group=protein_sequence.AccessionID, tau_POI__isnull=False)
            else:
                turnover_data = TurnoverData.objects.filter(Protein_Group=protein_sequence.AccessionID)
            a = sorted(turnover_data, key=lambda x: len(x.Stripped_Sequence), reverse=True)
            pos_dict = {}
            for i in a:
                i2 = protein_sequence.Sequence.index(i.Stripped_Sequence)
                for i3 in range(len(i.Stripped_Sequence)):
                    if i2+i3 not in pos_dict:
                        pos_dict[i2+i3] = []
                    pos_dict[i2+i3].append(i.id)
            data = {}
            for i in turnover_data:
                data[i.id] = {"id": i.id, "Precursor_Id": i.Precursor_Id, "Tissue": i.Tissue, "Engine": i.Engine, "tau_POI": i.tau_POI, "HalfLife_POI": i.HalfLife_POI, "Stripped_Sequence": i.Stripped_Sequence}
            print(data)
            return Response({"coverage": pos_dict, "turnover_data": data, "protein_sequence": protein_sequence.Sequence})
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SessionViewSets(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser)
    serializer_class = SessionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('id',)
    ordering = ('id',)
    filter_mappings = {
        "id": "id__exact",
        "user_id": "user_id__exact",
    }

    def get_queryset(self):
        return self.queryset


    def create(self, request, *args, **kwargs):
        current_user = request.user
        session = Session.objects.create(user=current_user, name=request.data["name"], details=request.data["details"], protein_group=request.data["protein_group"])
        session.save()
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, **kwargs):
        session = self.get_object()
        session.name = request.data['name']
        session.details = request.data['details']
        session.protein_group = request.data['protein_group']
        session.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, **kwargs):
        current_user = request.user
        session = self.get_object()
        if session.user != current_user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def user_only(self, request, pk=None):
        current_user = request.user
        queryset = Session.objects.filter(user=current_user)
        json_data = SessionSerializer(queryset, many=True).data
        return Response(json_data)
