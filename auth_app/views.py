from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from . import serializers

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    val = serializers.UserSerializer(data=request.data)
    if val.is_valid():
        val.save()
        return Response(val.data, status=status.HTTP_201_CREATED)
    return Response(val.errors, status=status.HTTP_400_BAD_REQUEST)