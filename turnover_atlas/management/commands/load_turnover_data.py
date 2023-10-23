import json
import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from turnover_atlas.models import TurnoverData, TurnoverDataValue
import pandas as pd

class Command(BaseCommand):
    """
    A command that read turnover data from tabulated txt file and store it in database using django model TurnoverData. This command would read the data in chunk of 50000 rows into a pandas dataframe and then convert the data from wide form to long form before inserting into the database.
    """
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the turnover tabulated txt file to be processed')

    def handle(self, *args, **options):
        file_path = options['file_path']
        data = pd.read_csv(file_path, sep="\t", chunksize=50000)
        fields = [f.name for f in TurnoverData._meta.get_fields()]
        pattern = re.compile(r"T(\d+)")
        for chunk in data:
            with transaction.atomic():
                sample_map = {}
                for c in chunk.columns:
                    match = pattern.search(c)
                    if match:
                        if match.group(0) not in sample_map:
                            sample_map[match.group(0)] = {"H": "", "L": "", "HL": ""}
                        if c.endswith("-H"):
                            sample_map[match.group(0)]["H"] = c
                        elif c.endswith("-L"):
                            sample_map[match.group(0)]["L"] = c
                        elif c.endswith("_HL"):
                            sample_map[match.group(0)]["HL"] = c

                for i, r in chunk.iterrows():
                    turnover_data = TurnoverData.objects.create(
                        Protein_Group=r["Protein.Group"],
                        Protein_Ids=r["Protein.Ids"],
                        Protein_Names=r["Protein.Names"],
                        Genes=r["Genes"],
                        Stripped_Sequence=r["Stripped.Sequence"],
                        Modified_Sequence=r["Modified.Sequence"],
                        Precursor_Id=r["Precursor.Id"],
                        Engine=r["Engine"],
                        Tissue=r["Tissue"],
                    )

                    for f in TurnoverData._meta.get_fields():
                        if f.get_internal_type != "TextField" and f.get_internal_type != "JSONField" and f.name in r.index:
                            if pd.isnull(r[f.name]):
                                setattr(turnover_data, f.name, None)
                            else:
                                setattr(turnover_data, f.name, r[f.name])

                    if not pd.isna(r["rs"]):
                        turnover_data.rs = json.dumps(r["rs"].split(";"))

                    turnover_data.save()
                    values = []
                    for k, v in sample_map.items():
                        value = TurnoverDataValue()
                        value.Sample_Name = k

                        if not pd.isna(r[v["H"]]):
                            value.SampleH = r[v["H"]]
                        if not pd.isna(r[v["L"]]):
                            value.SampleL = r[v["L"]]
                        if not pd.isna(r[v["HL"]]):
                            value.Sample_H_over_HL = r[v["HL"]]

                        value.meta_data = turnover_data
                        values.append(value)
                    TurnoverDataValue.objects.bulk_create(values)




