from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Cliente
from .serializers import ClienteWebhookSerializer


class ClientesWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteWebhookSerializer(clientes, many=True)
        return Response(
            {
                "total": clientes.count(),
                "clientes": serializer.data
            },
            status=status.HTTP_200_OK
        )
