from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

from .models import Device, DeviceAction, Home, SensorData
from .permissions import CanAccessDevice, CanAccessHome, CanDeleteDevice, user_has_home_access
from .serializers import DeviceActionSerializer, DeviceCommandCreateSerializer, DeviceSerializer, HomeMemberSerializer, HomeSerializer, SensorDataCreateSerializer, SensorDataSerializer
from .services import enqueue_device_action, record_sensor_reading


@extend_schema_view(
	list=extend_schema(tags=['homes'], summary='List homes', responses=HomeSerializer),
	retrieve=extend_schema(tags=['homes'], summary='Get home details', responses=HomeSerializer),
	create=extend_schema(tags=['homes'], summary='Create home', request=HomeSerializer, responses=HomeSerializer),
	update=extend_schema(tags=['homes'], summary='Update home', request=HomeSerializer, responses=HomeSerializer),
	partial_update=extend_schema(tags=['homes'], summary='Patch home', request=HomeSerializer, responses=HomeSerializer),
	destroy=extend_schema(tags=['homes'], summary='Delete home', responses={204: None}),
)
class HomeViewSet(viewsets.ModelViewSet):
	serializer_class = HomeSerializer
	permission_classes = [IsAuthenticated, CanAccessHome]

	def get_queryset(self):
		user = self.request.user
		queryset = Home.objects.select_related('owner').prefetch_related('memberships__user', 'devices')
		if user.is_superuser:
			return queryset
		return queryset.filter(Q(owner=user) | Q(memberships__user=user)).distinct()

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)

	@extend_schema(
		tags=['homes'],
		summary='List or add home members',
		request=HomeMemberSerializer,
		responses={200: HomeMemberSerializer(many=True), 201: HomeMemberSerializer},
	)
	@action(detail=True, methods=['get', 'post'], url_path='members')
	def members(self, request, pk=None):
		home = self.get_object()
		if request.method == 'GET':
			members = home.memberships.select_related('user').all()
			serializer = HomeMemberSerializer(members, many=True)
			return Response(serializer.data)

		if not user_has_home_access(request.user, home, write=True):
			return Response({'detail': 'You do not have permission to manage members for this home.'}, status=status.HTTP_403_FORBIDDEN)

		serializer = HomeMemberSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save(home=home)
		return Response(serializer.data, status=status.HTTP_201_CREATED)




@extend_schema_view(
	list=extend_schema(tags=['devices'], summary='List devices', responses=DeviceSerializer),
	retrieve=extend_schema(tags=['devices'], summary='Get device details', responses=DeviceSerializer),
	create=extend_schema(tags=['devices'], summary='Create device', request=DeviceSerializer, responses=DeviceSerializer),
	update=extend_schema(tags=['devices'], summary='Update device', request=DeviceSerializer, responses=DeviceSerializer),
	partial_update=extend_schema(tags=['devices'], summary='Patch device', request=DeviceSerializer, responses=DeviceSerializer),
	destroy=extend_schema(tags=['devices'], summary='Delete device', responses={204: None}),
)
class DeviceViewSet(viewsets.ModelViewSet):
	serializer_class = DeviceSerializer
	permission_classes = [IsAuthenticated, CanAccessDevice]

	def get_queryset(self):
		user = self.request.user
		queryset = Device.objects.select_related('home', 'home__owner').prefetch_related('readings', 'actions')
		if user.is_superuser:
			return queryset
		return queryset.filter(Q(home__owner=user) | Q(home__memberships__user=user)).distinct()

	def destroy(self, request, *args, **kwargs):
		device = self.get_object()
		permission = CanDeleteDevice()
		if not permission.has_object_permission(request, self, device):
			return Response({'detail': 'Only the home owner can delete this device.'}, status=status.HTTP_403_FORBIDDEN)
		return super().destroy(request, *args, **kwargs)

	@extend_schema(
		tags=['devices'],
		summary='List or create sensor readings for a device',
		request=SensorDataCreateSerializer,
		responses={200: SensorDataSerializer(many=True), 201: SensorDataSerializer},
	)
	@action(detail=True, methods=['get', 'post'], url_path='readings')
	def readings(self, request, pk=None):
		device = self.get_object()
		if request.method == 'GET':
			serializer = SensorDataSerializer(device.readings.all(), many=True)
			return Response(serializer.data)

		serializer = SensorDataCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		reading = record_sensor_reading(
			device=device,
			metric_name=serializer.validated_data['metric_name'],
			value=serializer.validated_data.get('value'),
			unit=serializer.validated_data.get('unit', ''),
			payload=serializer.validated_data.get('payload', {}),
			source='api',
		)
		return Response(SensorDataSerializer(reading).data, status=status.HTTP_201_CREATED)

	@extend_schema(tags=['devices'], summary='Get latest reading for a device', responses={200: SensorDataSerializer, 404: OpenApiResponse(description='No readings found')})
	@action(detail=True, methods=['get'], url_path='latest-reading')
	def latest_reading(self, request, pk=None):
		device = self.get_object()
		reading = device.readings.first()
		if reading is None:
			return Response({'detail': 'No readings found.'}, status=status.HTTP_404_NOT_FOUND)
		return Response(SensorDataSerializer(reading).data)

	@extend_schema(
		tags=['devices'],
		summary='List commands or enqueue a new device action',
		request=DeviceCommandCreateSerializer,
		responses={200: DeviceActionSerializer(many=True), 201: DeviceActionSerializer},
	)
	@action(detail=True, methods=['get', 'post'], url_path='actions')
	def actions(self, request, pk=None):
		device = self.get_object()
		if request.method == 'GET':
			serializer = DeviceActionSerializer(device.actions.all(), many=True)
			return Response(serializer.data)

		serializer = DeviceCommandCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		action = enqueue_device_action(
			device=device,
			action_type=serializer.validated_data['action_type'],
			user=request.user,
			payload=serializer.validated_data.get('payload', {}),
			source='api',
		)
		return Response(DeviceActionSerializer(action).data, status=status.HTTP_201_CREATED)




@extend_schema_view(
	list=extend_schema(tags=['device-actions'], summary='List device actions', responses=DeviceActionSerializer),
	retrieve=extend_schema(tags=['device-actions'], summary='Get device action', responses=DeviceActionSerializer),
)
class DeviceActionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = DeviceActionSerializer
	permission_classes = [IsAuthenticated, CanAccessDevice]

	def get_queryset(self):
		queryset = DeviceAction.objects.select_related('device', 'device__home', 'user')
		user = self.request.user
		if user.is_superuser:
			return queryset
		return queryset.filter(Q(device__home__owner=user) | Q(device__home__memberships__user=user)).distinct()




@extend_schema_view(
	list=extend_schema(tags=['readings'], summary='List sensor readings', responses=SensorDataSerializer),
	retrieve=extend_schema(tags=['readings'], summary='Get sensor reading', responses=SensorDataSerializer),
)
class SensorDataViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = SensorDataSerializer
	permission_classes = [IsAuthenticated, CanAccessDevice]

	def get_queryset(self):
		queryset = SensorData.objects.select_related('device', 'device__home')
		user = self.request.user
		if user.is_superuser:
			return queryset
		return queryset.filter(Q(device__home__owner=user) | Q(device__home__memberships__user=user)).distinct()
