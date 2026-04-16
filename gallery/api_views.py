from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Painting
from .serializers import PaintingSerializer


class PaintingListAPIView(APIView):
    def get(self, request):
        queryset = Painting.objects.filter(is_active=True).order_by("-date")
        serializer = PaintingSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class PaintingDetaiAPIView(APIView):
    def get(self, request, pk):
        painting = get_object_or_404(Painting, id=pk, is_active=True)
        serializer = PaintingSerializer(
            painting,
            context={"request": request},
        )
        return Response(serializer.data)
