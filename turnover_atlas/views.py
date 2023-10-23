from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from turnover_atlas.models import TurnoverData, TurnoverDataValue

class AvailableTissues(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        """Get all unique tissues from TurnoverData Tissue field"""
        tissues = TurnoverData.objects.order_by("Tissue").values_list("Tissue").distinct("Tissue")
        return Response(tissues)