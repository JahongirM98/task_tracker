from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.filter(user=user).order_by("start_at")
        # фильтр диапазона для календаря: ?start=ISO&end=ISO
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start and end:
            start_dt = parse_datetime(start)
            end_dt = parse_datetime(end)
            if start_dt and end_dt:
                # пересечение любого события с окном [start, end]
                qs = qs.filter(
                    Q(start_at__lt=end_dt) & Q(end_at__gt=start_dt)
                )
        return qs

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = Task.Status.DONE
        task.save(update_fields=["status"])
        return Response(self.get_serializer(task).data)
