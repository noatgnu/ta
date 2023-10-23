import json
import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from turnover_atlas.models import SampleGroupMetadata
import pandas as pd

class Command(BaseCommand):
    """
    A command that remove all rows from SampleGroupMetadata table and load the data from the provided csv file
    """
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the sample metadata csv file to be processed')

    def handle(self, *args, **options):
        file_path = options['file_path']
        data = pd.read_csv(file_path, sep=",")
        with transaction.atomic():
            SampleGroupMetadata.objects.all().delete()
            for i, r in data.iterrows():
                SampleGroupMetadata.objects.create(
                    Sample_Name=r["SampleID"],
                    Sample_Label=r["Labelling"],
                    Days=r["Days"],
                    Replicate=r["Replicate"]
                )