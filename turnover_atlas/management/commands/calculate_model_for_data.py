import json
import re

import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from turnover_atlas.models import TurnoverData, ModelParameters, SampleGroupMetadata
import pandas as pd
from turnover_atlas.utils import func_pulse
class Command(BaseCommand):
    """
    A command that use data from ModelParameters table to calculate values for kinetic modelling of turnover data
    """
    def add_arguments(self, parser):
        parser.add_argument('days', type=int, help='Days for kinetic modelling to be processed')
    def handle(self, *args, **options):
        with transaction.atomic():
            for i in TurnoverData.objects.all():
                if i.tau_POI is not None:
                    params = ModelParameters.objects.filter(Engine=i.Engine, Tissue=i.Tissue).first()
                    if params is not None:
                        pulse = []
                        available_days = []
                        for i2 in i.values.all():
                            if i2.Sample_H_over_HL is not None:
                                s = SampleGroupMetadata.objects.get(Sample_Name=i2.Sample_Name)
                                if s.Days not in available_days:
                                    available_days.append(s.Days)
                        if 0 not in available_days:
                            available_days.append(0)
                        if options["days"] not in available_days:
                            available_days.append(options["days"])
                        available_days.sort()
                        for d in available_days:
                            day = d
                            value = func_pulse(d, params.a, params.b, params.r, i.tau_POI)
                            if np.isinf(value):
                                value = 1.0
                            if i.tau_POI_upper_bound is not None:
                                tau_POI_upper_bound = func_pulse(d, params.a, params.b, params.r, i.tau_POI_upper_bound)
                                if np.isinf(tau_POI_upper_bound):
                                    tau_POI_upper_bound = 1.0
                            else:
                                tau_POI_upper_bound = None
                            if i.tau_POI_lower_bound is not None:
                                tau_POI_lower_bound = func_pulse(d, params.a, params.b, params.r, i.tau_POI_lower_bound)
                                if np.isinf(tau_POI_lower_bound):
                                    tau_POI_lower_bound = 1.0
                            else:
                                tau_POI_lower_bound = None
                            data = {"value": value, "day": day, "tau_POI_upper_bound": tau_POI_upper_bound, "tau_POI_lower_bound": tau_POI_lower_bound}
                            pulse.append(data)
                        i.tau_model = pulse
                        i.save()