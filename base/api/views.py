from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from base.models import Room
from.serializers import RoomSerializer

@api_view(['GET'])
def get_routes(request):
    routes = [
        'GET / api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)

@api_view(['GET', 'POST'])
def get_rooms(request):

    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_room(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)