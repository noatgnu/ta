import json
import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from turnover_atlas.models import TurnoverData, AccessionIDMap
import pandas as pd

class Command(BaseCommand):
    """
    A command that refresh acc and gene map data by removing all rows in AccessionIDMap then read and extract unique Protein_Group and Genes combinations from TurnoverData and insert into the table.
    """

    def handle(self, *args, **options):
        with transaction.atomic():
            AccessionIDMap.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all mapping data'))
        t = TurnoverData.objects.order_by("Protein_Group").values_list("Protein_Group", "Genes").distinct(
            "Protein_Group", "Genes")
        with transaction.atomic():
            for i in t:
                AccessionIDMap.objects.create(Protein_Group=i[0], Genes=i[1])
        self.stdout.write(self.style.SUCCESS('Successfully inserted all mapping data'))