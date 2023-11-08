from rest_framework import serializers

from turnover_atlas.models import TurnoverData, TurnoverDataValue, AccessionIDMap, SampleGroupMetadata, ModelParameters, \
    ProteinSequence


class TurnoverDataSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    def get_values(self, obj):
        return TurnoverDataValueSerializer(obj.values.all(), many=True).data


    class Meta:
        model = TurnoverData
        fields = (
            'id',
            'Protein_Group',
            'Protein_Ids',
            'Protein_Names',
            'Genes',
            'Proteotypic',
            'Stripped_Sequence',
            'Modified_Sequence',
            'Precursor_Id',
            'n_Samples',
            'n_TimePoints',
            'tau_POI',
            'tau_POI_lower_bound',
            'tau_POI_upper_bound',
            'tau_POI_range',
            'tau_POI_range_relative',
            'HalfLife_POI',
            'HalfLife_POI_lower_bound',
            'HalfLife_POI_upper_bound',
            'HalfLife_POI_range',
            'HalfLife_POI_range_relative',
            'rss',
            'rs',
            'AverageRSS',
            'Engine',
            'Tissue',
            'values',
            'tau_model',
        )

class TurnoverDataValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurnoverDataValue
        fields = (
            'id',
            'Sample_Name',
            'SampleH',
            'SampleL',
            'Sample_H_over_HL',
            'meta_data',
        )

class AccessionIDMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessionIDMap
        fields = (
            'id',
            'Protein_Group',
            'Genes',
        )


class SampleGroupMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleGroupMetadata
        fields = (
            'id',
            'Sample_Name',
            'Sample_Label',
            'Days',
            'Replicate'
        )

class ModelParametersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelParameters
        fields = (
            'id',
            'a',
            'b',
            'r',
            'n',
            'eps',
            'min',
            'Engine',
            'Tissue',
            'k_pool'
        )

class ProteinSequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProteinSequence
        fields = (
            'id',
            'AccessionID',
            'Sequence',
        )