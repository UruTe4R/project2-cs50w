from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from PIL import Image

from .models import User, Listing, Bid, Comment, Reply

class Listing_form(forms.ModelForm):
    class Meta():
        model =  Listing
        fields = ['title', 'description', 'photo', 'first_price']

        first_price = forms.DecimalField(max_digits=10, decimal_places=2)
    def clean_photo(self):
        photo = self.cleaned_data["photo"]
        img = Image.open(photo)
        max_width, max_height = 500, 500
        img.thumbnail((max_width, max_height), Image.ANTIALIAS)
        img.save(photo, format=img.format)

        return photo



def index(request):
    if request.method == "POST":
        ...
    else:
        listings = Listing.objects.all()
        return render(request, "auctions/index.html", {
            "listings": listings
        })

@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html")

@login_required
def add_listing(request):
    if request.method == "POST":
        form = Listing_form(request.POST)
        # is form valid?
        if not form.is_valid():
            return render(request, "auctions/add_listing.html", {
                "form": form
            })
        #save to database, w/owner
        listing = form.save(commit=False)
        listing.owner = request.user
        listing.save()

        return render(request, "auctions/index.html", { **form.cleaned_data

        })
    else:
        listing_form = Listing_form()
        return render(request, "auctions/add_listing.html", {
            "form": listing_form
        })

@login_required
def categories(request):
    return render(request, "auctions/categories.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
