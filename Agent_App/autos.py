from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Auto
from .serializers import AutoWebhookSerializer


class AutosWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        autos = Auto.objects.all()
        serializer = AutoWebhookSerializer(autos, many=True)
        return Response(
            {
                "total": autos.count(),
                "autos": serializer.data
            },
            status=status.HTTP_200_OK
        )
