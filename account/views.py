from django.shortcuts import render
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import logout

def index(request):
    return render(request, "account/index.html")

def login(request):
    return render(request, "account/login.html")

def logout(request):
    logout(request)

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return render(request, "account/index.html",{
                "message": "User created successfully", 
                "user": user
                })
        else:
            return render(request, "account/register.html", {
                #"message": "Error creating user",
                "form": form
            })
    return render(request, "account/register.html", {
        "form": RegisterForm()})

#create a reposter in github and push the code and name it
#finish the login and logout fuctions and create the templates for them
