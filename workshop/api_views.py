from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Workshop
from .serializers import WorkshopSerializer


class WorkshopListAPIView(APIView):
    def get(self, request):
        queryset = Workshop.objects.all().order_by("-created_at")
        serializer = WorkshopSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class WorkshopDetaiAPIView(APIView):
    def get(self, request, pk):
        workshop = get_object_or_404(Workshop, pk=pk)
        serializer = WorkshopSerializer(
            workshop,
            context={"request": request},
        )
        return Response(serializer.data)
