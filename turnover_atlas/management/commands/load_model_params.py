import json
import re

import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from turnover_atlas.models import ModelParameters
import pandas as pd
from turnover_atlas.utils import func_kpool, func_pulse
class Command(BaseCommand):
    """
    A command that remove all rows from sample model table and load data from provided txt files
    """
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the modelling params txt file to be processed')
        parser.add_argument('days', type=int, help='Days for kinetic modelling to be processed')
    def handle(self, *args, **options):
        file_path = options['file_path']
        data = pd.read_csv(file_path, sep="\t")
        with transaction.atomic():
            ModelParameters.objects.all().delete()
            for i, r in data.iterrows():
                kpool = []
                for i in range(0, options['days']+1, 5):
                    value = func_kpool(i, r["a"], r["b"], r["r"])
                    if pd.isnull(value):
                        continue
                    if np.isinf(value):
                        value = 1.0
                    data = {"value": value, "day": i}
                    kpool.append(data)
                ModelParameters.objects.create(
                    a=r["a"],
                    b=r["b"],
                    r=r["r"],
                    n=r["n"],
                    eps=r["eps"],
                    min=r["min"],
                    Engine=r["Engine"],
                    Tissue=r["Tissue"],
                    k_pool=kpool
                )


