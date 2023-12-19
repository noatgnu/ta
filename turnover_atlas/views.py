import numpy as np
import pandas as pd
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from turnover_atlas.models import TurnoverData, TurnoverDataValue, ModelParameters
from turnover_atlas.utils import func_pulse, func_kpool


class AvailableTissues(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """Get all unique tissues from TurnoverData Tissue field"""
        tissues = TurnoverData.objects.order_by("Tissue").values_list("Tissue").distinct("Tissue")
        return Response(tissues)


class ModelData(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        engine = self.request.data["Engine"]
        tissue = self.request.data["Tissue"]
        tau_POI = self.request.data["tau_POI"]
        tau_POI_lower_bound = self.request.data["tau_POI_lower_bound"]
        tau_POI_upper_bound = self.request.data["tau_POI_upper_bound"]
        days = self.request.data["Data"]
        #print(engine, tissue, tau_POI, tau_POI_lower_bound, tau_POI_upper_bound, days)
        params = ModelParameters.objects.filter(Engine=engine, Tissue=tissue).first()
        #print(params)
        #calculate kpool for 5-minutes interval from 0 to 50 days where the unit is days and return a json arrays of kpool value and day value
        kpool = []
        if params is not None:
            for t in range(0, 50, 5):
                day = t/60/24
                value = func_kpool(t, params.a, params.b, params.r)
                if pd.isnull(value):
                    continue
                if np.isinf(value):
                    value = 1.0
                data = {"value": value, "day": day}
                kpool.append(data)
            pulse = []
            days.sort()
            for d in days:
                day = d
                value = func_pulse(d, params.a, params.b, params.r, tau_POI)
                tau_POI_upper_bound = func_pulse(d, params.a, params.b, params.r, tau_POI_upper_bound)
                tau_POI_lower_bound = func_pulse(d, params.a, params.b, params.r, tau_POI_lower_bound)
                data = {"value": value, "day": day}
                if pd.notnull(tau_POI_upper_bound):
                    data['tau_POI_upper_bound'] = tau_POI_upper_bound
                if pd.notnull(tau_POI_lower_bound):
                    data['tau_POI_lower_bound'] = tau_POI_lower_bound

                pulse.append(data)
            return Response({
                "kpool": kpool,
                "pulse": pulse
            })
        else:
            return Response({
                "kpool": [],
                "pulse": []
            })

    def get(self, request, format=None):
        step = request.query_params.get("step", 5)
        tissue = request.query_params.get("tissue", None)
        engine = request.query_params.get("engine", None)
        start = request.query_params.get("start", 0)
        end = request.query_params.get("end", 50)
        params = ModelParameters.objects.filter(Engine=engine, Tissue=tissue).first()
        kpool = []
        if params is not None:
            current_day = int(start)
            step = float(step)
            while current_day <= int(end):
                value = func_kpool(current_day, params.a, params.b, params.r)
                if pd.isnull(value):
                    continue
                if np.isinf(value):
                    value = 1.0
                data = {"value": value, "day": current_day}
                kpool.append(data)
                current_day += step

            return Response({
                "kpool": kpool,
            })
        else:
            return Response({
                "kpool": [],
            })
