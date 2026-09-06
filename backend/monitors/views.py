from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.

from .models import Monitor
from .serializers import MonitorSerializer


class MonitorListView(APIView):
    
    def get(self, request):
        monitors = Monitor.objects.all()
        serializer = MonitorSerializer(monitors, many=True)

        return Response(serializer.data)

    
