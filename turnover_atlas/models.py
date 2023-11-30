from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class TurnoverData(models.Model):
    """A data model for storing turnover data with the following column:
    - Protein_Group
    - Protein_Ids
    - Protein_Names
    - Genes
    - Proteotypic
    - Stripped_Sequence
    - Modified_Sequence
    - Precursor_Id
    - n_Samples
    - n_TimePoints
    - tau_POI
    - tau_POI_lower_bound
    - tau_POI_upper_bound
    - tau_POI_range
    - tau_POI_range_relative
    - HalfLife_POI
    - HalfLife_POI_lower_bound
    - HalfLife_POI_upper_bound
    - HalfLife_POI_range
    - HalfLife_POI_range_relative
    - rss
    - rs
    - Sample_Name
    - SampleL
    - SampleH
    - Sample_H_over_HL
    - AverageRSS
    - Engine
    - Tissue

    """

    Protein_Group = models.TextField(blank=False, null=False, db_index=True)
    Protein_Ids = models.TextField(blank=True, null=True)
    Protein_Names = models.TextField(blank=True, null=True)
    Genes = models.TextField(blank=False, null=False, db_index=True)
    Proteotypic = models.IntegerField(blank=True, null=True)
    Stripped_Sequence = models.TextField(blank=True, null=True)
    Modified_Sequence = models.TextField(blank=True, null=True)
    Precursor_Id = models.TextField(blank=True, null=True)
    n_Samples = models.IntegerField(blank=True, null=True)
    n_TimePoints = models.IntegerField(blank=True, null=True)
    tau_POI = models.FloatField(blank=True, null=True)
    tau_POI_lower_bound = models.FloatField(blank=True, null=True)
    tau_POI_upper_bound = models.FloatField(blank=True, null=True)
    tau_POI_range = models.FloatField(blank=True, null=True)
    tau_POI_range_relative = models.FloatField(blank=True, null=True)
    HalfLife_POI = models.FloatField(blank=True, null=True)
    HalfLife_POI_lower_bound = models.FloatField(blank=True, null=True)
    HalfLife_POI_upper_bound = models.FloatField(blank=True, null=True)
    HalfLife_POI_range = models.FloatField(blank=True, null=True)
    HalfLife_POI_range_relative = models.FloatField(blank=True, null=True)
    rss = models.FloatField(blank=True, null=True)
    rs = models.JSONField(blank=True, null=True)
    AverageRSS = models.FloatField(blank=True, null=True)
    Engine = models.TextField(blank=True, null=True)
    Tissue = models.TextField(blank=True, null=True)
    tau_model = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["id"]
        app_label = "turnover_atlas"

    def __str__(self):
        return f"{self.Protein_Group} {self.Tissue}"

    def __repr__(self):
        return f"{self.Protein_Group} {self.Tissue}"


class TurnoverDataValue(models.Model):
    Sample_Name = models.TextField(blank=True, null=True)
    SampleL = models.FloatField(blank=True, null=True)
    SampleH = models.FloatField(blank=True, null=True)
    Sample_H_over_HL = models.FloatField(blank=True, null=True)
    meta_data = models.ForeignKey(
        TurnoverData, on_delete=models.CASCADE, related_name="values"
    )

    class Meta:
        app_label = "turnover_atlas"
        ordering = ["id"]


class AccessionIDMap(models.Model):
    Protein_Group = models.TextField(blank=True, null=True)
    Genes = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "turnover_atlas"
        ordering = ["id"]


class SampleGroupMetadata(models.Model):
    Sample_Name = models.TextField(blank=True, null=True)
    Sample_Label = models.TextField(blank=True, null=True)
    Days = models.IntegerField(blank=True, null=True)
    Replicate = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = "turnover_atlas"
        ordering = ["id"]

class ModelParameters(models.Model):
    a = models.FloatField(blank=False, null=False)
    b = models.FloatField(blank=False, null=False)
    r = models.FloatField(blank=False, null=False)
    n = models.FloatField(blank=False, null=False)
    eps = models.FloatField(blank=False, null=False)
    min = models.FloatField(blank=False, null=False)
    Engine = models.TextField(blank=False, null=False)
    Tissue = models.TextField(blank=False, null=False)
    k_pool = models.JSONField(blank=True, null=True)

    class Meta:
        app_label = "turnover_atlas"
        ordering = ["id"]


class ProteinSequence(models.Model):
    """
    A Model to store protein sequences with a column storing uniprot id and another storing the sequence
    """
    AccessionID = models.TextField(blank=False, null=False, db_index=True)
    Sequence = models.TextField(blank=False, null=False)

    class Meta:
        app_label = "turnover_atlas"
        ordering = ["AccessionID"]


class Session(models.Model):
    details = models.JSONField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    protein_group = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="protein_sessions", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "turnover_atlas"
        ordering = ["id"]

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


