from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
# for image resizing
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
# path for image saving
from django.conf import settings
import os

from .models import User, Listing, Bid, Comment, Reply, Categories

""" 2024-12-22 一旦ここで色んな動画を見あさろうと思う。まだgitにセーブしていない
画像をテーブルに保存したいが、保存されるのが毎度error.pngになる。なぜか？
一度画像のサイズを既定のサイズに変える関数を消したがどこかに導入したい。
CSSもうまいこと行かないからそこもどうにかしないと。。。
    2024-12-23
    image upload worked. with enctype attribute
"""

class ListingForm(forms.ModelForm):
    class Meta:
        model =  Listing
        fields = ['title', 'description', 'image_path', 'image_URL', 'first_price', 'category_name']
        # set labels
        labels= {"first_price": "Starting Price($)",
                 "image_path": "Upload Image",
                 "image_URL": "Image URL"
                 }

        first_price = forms.DecimalField(max_digits=10, decimal_places=2)
    
    def clean_image_path(self):
        print("clean_image_path called")
        # check if image is uploaded
        if not (uploaded_file := self.cleaned_data["image_path"]):
            return uploaded_file

        # open the image file with PIL
        img = Image.open(uploaded_file)

        # set the resizing width and height
        max_width, max_height = 500, 500

        origina_width, original_height = img.size
        # resize image if it's larger than the max size
        if origina_width > max_width or original_height > max_height:
            # .thumbnail() resizes the image with the same proportion
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        else:
            # .resize() does not change the original
            img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save the resized image to a memory buffer
        # BytesIO is python's module to create in-memory binary stream
        # create temporal buffer from BytesIO()
        buffer = BytesIO()
        img.save(buffer, format="PNG") 

        #.seek() will move the file pointer to the arugument, in this case 0 means beginning
        buffer.seek(0)
        
        # Create a ContentFile from the buffer and assign it to the field
        # ContentFile() can convert file object to django-compatible file
        img_content = ContentFile(buffer.read())
        img_content.name = uploaded_file.name
        
        # Save the image content to the model field
        self.cleaned_data["image_path"] = img_content
        
        return img_content  # Return the modified image content




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
        form = ListingForm(request.POST, request.FILES)
        print("request.FILES:", request.FILES)
        # is form valid?
        if not form.is_valid():
            return render(request, "auctions/add_listing.html", {
                "form": form
            })
        #save to database, w/owner
        listing = form.save(commit=False)
        listing.owner = request.user
        listing.save()
        print(f"Image path: {os.path.join(settings.MEDIA_ROOT, listing.image_path.name)}")
        return HttpResponseRedirect(reverse("index"))
    else:
        listing_form = ListingForm()
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
