from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.http import JsonResponse
import json


def signup(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "User already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        return JsonResponse({"message": "User created successfully"})


from django.contrib.auth import authenticate, login

def user_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"message": "Login successful"})
        return JsonResponse({"error": "Invalid credentials"}, status=400)
