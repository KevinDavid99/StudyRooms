from multiprocessing import AuthenticationError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from.forms import RoomForm, UserForm, MyUserCreationForm
# Create your views here.


# rooms = [
#     {'id': 1, 'name': 'Lets Learn Python'},
#     {'id': 2, 'name': 'Design some stuffs'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]

def login_page(request):
    page = 'login'
    # we dont want the user relogging in, so...
    if request.user.is_authenticated:
        return redirect('home')

    # making users to log in
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        #checking if the user exist or not
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        #if the user exist
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "Username OR password doses not exist" )

    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def logout_page(request):
    logout(request)
    return redirect('home')

def register_user(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registeration')
            
    return render(request, 'base/login_register.html', {'form':form})


def home(request):
    # q = request.GET.get('q')
    if request.GET.get('q') != None:
         q = request.GET.get('q')
    else:
        q=''

    rooms = Room.objects.filter( Q(topic__name__icontains = q)|Q(name__icontains = q)|Q(description__icontains=q)) # for the search functionality
    
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))#for recent activity

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()

    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count,'room_messages':room_messages }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()  #commenting in a room post 
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room, 
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room':room, 'room_messages':room_messages, 'participants':participants}  
    return render(request, 'base/room.html', context)

@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name )
        # form = RoomForm(request.POST)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user # let the backend know the user who is posting
        #     room.save()
        return redirect('home')

    context = {'form': form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='/login')
def update_room(request ,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    # Restricting a user from logging in into someones account with their id
    if request.user != room.host:
        return HttpResponse('<h2>You are not allowed here, gettat!!</h2>')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name )
        room.name = request.POST.get('name')
        room.topic =topic
        room.description = request.POST.get('description')
        room.save()
        return redirect ('home')

    context = {'form': form, 'topics':topics, 'room':room}
    return render (request, 'base/room_form.html', context)

@login_required(login_url='/login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    # Restricting a user from logging in into someones account with their id
    if request.user != room.host:
        return HttpResponse('<h2>You are not allowed here, gettat!!</h2>')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})



@login_required(login_url='/login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    # Restricting a user from logging in into someones account with their id
    if request.user != message.user:
        return HttpResponse('<h2>You are not allowed here, gettat!!</h2>')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='/login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid(): 
            form.save()
        return redirect('user-profile', pk=user.id)


    return render(request, 'base/update_user.html', {'form':form})


def topic_page(request):
    q = request.GET.get('q')
    if request.GET.get('q') != None:
         q = request.GET.get('q')
    else:
        q=''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})


def activity_page(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages':room_messages})