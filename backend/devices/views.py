from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema, extend_schema_view

from .models import Device, DeviceAction, Home, Room, SensorData
from .permissions import CanAccessDevice, CanAccessHome, CanAccessRoom, CanDeleteDevice, user_has_home_access
from .serializers import DeviceActionSerializer, DeviceCommandCreateSerializer, DeviceSerializer, HomeMemberSerializer, HomeSerializer, RoomSerializer, SensorDataCreateSerializer, SensorDataSerializer
from .services import enqueue_device_action, record_sensor_reading


ROOM_ID_QUERY_PARAMETER = OpenApiParameter(
	name='room_id',
	type=OpenApiTypes.INT,
	location=OpenApiParameter.QUERY,
	required=False,
	description='Filter devices by room id.',
)

HOME_ID_QUERY_PARAMETER = OpenApiParameter(
	name='home_id',
	type=OpenApiTypes.INT,
	location=OpenApiParameter.QUERY,
	required=False,
	description='Filter rooms by home id.',
)

HOME_MEMBER_CREATE_EXAMPLE = OpenApiExample(
	'Add home member',
	value={
		'user_id': 12,
		'role': 'member',
		'can_manage_devices': False,
	},
	request_only=True,
)

HOME_MEMBER_RESPONSE_EXAMPLE = OpenApiExample(
	'Home member response',
	value={
		'id': 21,
		'home': 1,
		'user': {
			'id': 12,
			'first_name': 'Jan',
			'last_name': 'Kowalski',
		},
		'role': 'member',
		'can_manage_devices': False,
		'created_at': '2026-05-24T10:00:00Z',
	},
	response_only=True,
)

ROOM_CREATE_EXAMPLE = OpenApiExample(
	'Create room',
	value={
		'home_id': 1,
		'name': 'Living Room',
		'description': 'Main living area',
	},
	request_only=True,
)

ROOM_RESPONSE_EXAMPLE = OpenApiExample(
	'Room response',
	value={
		'id': 7,
		'home': 1,
		'name': 'Living Room',
		'description': 'Main living area',
		'created_at': '2026-05-24T10:00:00Z',
		'updated_at': '2026-05-24T10:00:00Z',
	},
	response_only=True,
)

DEVICE_CREATE_EXAMPLE = OpenApiExample(
	'Create device',
	value={
		'home_id': 1,
		'room_id': 7,
		'name': 'Thermometer Kitchen',
		'device_type': 'thermometer',
		'hardware_id': 'hw-thermo-001',
		'is_active': True,
		'current_state': 21.5,
		'state_payload': {'battery': 95},
	},
	request_only=True,
)

DEVICE_RESPONSE_EXAMPLE = OpenApiExample(
	'Device response',
	value={
		'id': 31,
		'home_id': 1,
		'room': {
			'id': 7,
			'name': 'Living Room',
			'description': 'Main living area',
		},
		'room_id': 7,
		'name': 'Thermometer Kitchen',
		'device_type': 'thermometer',
		'hardware_id': 'hw-thermo-001',
		'status': 'unknown',
		'is_active': True,
		'current_state': 21.5,
		'state_payload': {'battery': 95},
		'certificate_fingerprint': None,
		'last_seen_at': None,
		'created_at': '2026-05-24T10:00:00Z',
		'updated_at': '2026-05-24T10:00:00Z',
	},
	response_only=True,
)

HOME_DEVICES_FILTER_EXAMPLE = OpenApiExample(
	'Filter by room',
	value=7,
	parameter_only='room_id',
)


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
		queryset = Home.objects.select_related('owner').prefetch_related('memberships__user', 'devices', 'rooms')
		if user.is_superuser:
			return queryset
		return queryset.filter(Q(owner=user) | Q(memberships__user=user)).distinct()

	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)

	@extend_schema(
		tags=['homes'],
		summary='List or add home members',
		request=HomeMemberSerializer,
		examples=[HOME_MEMBER_CREATE_EXAMPLE, HOME_MEMBER_RESPONSE_EXAMPLE],
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

	@extend_schema(
		tags=['homes'],
		summary='Get, update or delete a home member',
		request=HomeMemberSerializer,
		examples=[HOME_MEMBER_RESPONSE_EXAMPLE, HOME_MEMBER_CREATE_EXAMPLE],
		responses={200: HomeMemberSerializer, 204: None},
	)
	@action(detail=True, methods=['get', 'put', 'delete'], url_path=r'members/(?P<member_id>[^/.]+)')
	def member(self, request, pk=None, member_id=None):
		home = self.get_object()
		member = home.memberships.select_related('user').filter(pk=member_id).first()
		if member is None:
			return Response({'detail': 'Home member not found.'}, status=status.HTTP_404_NOT_FOUND)

		if request.method == 'GET':
			serializer = HomeMemberSerializer(member)
			return Response(serializer.data)

		if not user_has_home_access(request.user, home, write=True):
			return Response({'detail': 'You do not have permission to manage members for this home.'}, status=status.HTTP_403_FORBIDDEN)

		if request.method == 'DELETE':
			member.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)

		serializer = HomeMemberSerializer(member, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)

	@extend_schema(
		tags=['homes'],
		summary='List devices for a home',
		parameters=[ROOM_ID_QUERY_PARAMETER],
		examples=[HOME_DEVICES_FILTER_EXAMPLE],
		responses=DeviceSerializer(many=True),
	)
	@action(detail=True, methods=['get'], url_path='devices')
	def devices(self, request, pk=None):
		home = self.get_object()
		queryset = home.devices.select_related('room', 'room__home').all()
		room_id = request.query_params.get('room_id')
		if room_id:
			queryset = queryset.filter(room_id=room_id)
		return Response(DeviceSerializer(queryset, many=True).data)


@extend_schema_view(
	list=extend_schema(tags=['rooms'], summary='List rooms', parameters=[HOME_ID_QUERY_PARAMETER], examples=[ROOM_RESPONSE_EXAMPLE], responses=RoomSerializer(many=True)),
	retrieve=extend_schema(tags=['rooms'], summary='Get room details', examples=[ROOM_RESPONSE_EXAMPLE], responses=RoomSerializer),
	create=extend_schema(tags=['rooms'], summary='Create room', request=RoomSerializer, examples=[ROOM_CREATE_EXAMPLE, ROOM_RESPONSE_EXAMPLE], responses=RoomSerializer),
	update=extend_schema(tags=['rooms'], summary='Update room', request=RoomSerializer, examples=[ROOM_CREATE_EXAMPLE, ROOM_RESPONSE_EXAMPLE], responses=RoomSerializer),
	partial_update=extend_schema(tags=['rooms'], summary='Patch room', request=RoomSerializer, examples=[ROOM_CREATE_EXAMPLE, ROOM_RESPONSE_EXAMPLE], responses=RoomSerializer),
	destroy=extend_schema(tags=['rooms'], summary='Delete room', responses={204: None}),
)
class RoomViewSet(viewsets.ModelViewSet):
	serializer_class = RoomSerializer
	permission_classes = [IsAuthenticated, CanAccessRoom]

	def get_queryset(self):
		user = self.request.user
		queryset = Room.objects.select_related('home', 'home__owner').prefetch_related('devices')
		home_id = self.request.query_params.get('home_id')
		if home_id:
			queryset = queryset.filter(home_id=home_id)
		if user.is_superuser:
			return queryset
		return queryset.filter(Q(home__owner=user) | Q(home__memberships__user=user)).distinct()

	def perform_create(self, serializer):
		serializer.save()


@extend_schema_view(
	list=extend_schema(tags=['devices'], summary='List devices', parameters=[ROOM_ID_QUERY_PARAMETER], examples=[HOME_DEVICES_FILTER_EXAMPLE], responses=DeviceSerializer(many=True)),
	retrieve=extend_schema(tags=['devices'], summary='Get device details', examples=[DEVICE_RESPONSE_EXAMPLE], responses=DeviceSerializer),
	create=extend_schema(tags=['devices'], summary='Create device', request=DeviceSerializer, examples=[DEVICE_CREATE_EXAMPLE, DEVICE_RESPONSE_EXAMPLE], responses=DeviceSerializer),
	update=extend_schema(tags=['devices'], summary='Update device', request=DeviceSerializer, examples=[DEVICE_CREATE_EXAMPLE, DEVICE_RESPONSE_EXAMPLE], responses=DeviceSerializer),
	partial_update=extend_schema(tags=['devices'], summary='Patch device', request=DeviceSerializer, examples=[DEVICE_CREATE_EXAMPLE, DEVICE_RESPONSE_EXAMPLE], responses=DeviceSerializer),
	destroy=extend_schema(tags=['devices'], summary='Delete device', responses={204: None}),
)
class DeviceViewSet(viewsets.ModelViewSet):
	serializer_class = DeviceSerializer
	permission_classes = [IsAuthenticated, CanAccessDevice]

	def get_queryset(self):
		user = self.request.user
		queryset = Device.objects.select_related('home', 'home__owner', 'room', 'room__home').prefetch_related('readings', 'actions')
		room_id = self.request.query_params.get('room_id')
		if room_id:
			queryset = queryset.filter(room_id=room_id)
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
