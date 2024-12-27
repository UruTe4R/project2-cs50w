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

""" 
    2024-12-22 一旦ここで色んな動画を見あさろうと思う。まだgitにセーブしていない
    画像をテーブルに保存したいが、保存されるのが毎度error.pngになる。なぜか？
    一度画像のサイズを既定のサイズに変える関数を消したがどこかに導入したい。
    CSSもうまいこと行かないからそこもどうにかしないと。。。

    2024-12-23
    image upload worked. with enctype attribute
    need to see if works with add image from url
    created "watchlist" field to User class
    CSS to index.html

    2024-12-24
    start from watchlist implementation!
    when accessing request.user, is_authenticated better be called <- NO!!
    i forgot login_required decorator... 

    finished listing's price in listing.html 
    2025-12-25
    implement listing especially bids
    2025-12-26
    implement categories
    maybe implement comment and reply
"""

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        labels = {'comment': ''}
        comment = forms.CharField(widget=forms.Textarea(attrs={
            'class': 'comment_input',
            'placeholder': 'Comment',
            'max_length': 500
        }))

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["current_bid"]
        labels = {"current_bid": ""}
        widgets = {
            "current_bid": forms.TextInput(attrs={
                'class': 'bid_input',
                'placeholder': 'Bid'
            })
        }

        

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image_path', 'image_URL', 'first_price', 'category_name']
        # set labels
        labels= {"first_price": "Starting Price($)",
                 "image_path": "Upload Image",
                 "image_URL": "Image URL"
                 }


    def clean_first_price(self):
        """
        check if price is positive
        """
        price = self.cleaned_data["first_price"]
        if price < 0:
            raise forms.ValidationError("Price must be positive value.")
        return price
    

    def clean_image_path(self):
        """
        set image size to fixed width * size

        i implemented this to change the bytes of original image
        so that it is more sustainable
        but i figured i do not need this because i might wanna make image bigger in listing...
        """
        print("clean_image_path called")
        # check if image is uploaded
        if not (uploaded_file := self.cleaned_data["image_path"]):
            return uploaded_file

        # open the image file with PIL
        img = Image.open(uploaded_file)

        # set the resizing width and height
        max_width, max_height = 500, 300

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
        # get all listings and order by creation date desc with "-"
        listings = Listing.objects.all().order_by("-creation_date")
        latest_bids = []
        for listing in listings:
            latest_bid = Bid.objects.filter(target_listing=listing).order_by("-bid_date").first()
            latest_bids.append(latest_bid)

        if request.user.is_authenticated:
            watchlist_count = request.user.watchlist.all().count()
        else:
            return HttpResponseRedirect(reverse("login"))
        return render(request, "auctions/index.html", {
            "listings": listings,
            "latest_bids": latest_bids,
            "watchlist_count": watchlist_count
        })

@login_required
def watchlist(request):
    watchlist_count = request.user.watchlist.all().count()
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
        "watchlist_count": watchlist_count
    })

@login_required
def add_watchlist(request, listing_id):
    # POST
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        if request.user.watchlist.filter(pk=listing_id).exists():
            request.user.watchlist.remove(listing)
        else:
            request.user.watchlist.add(listing)
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    
                
    # GET
    # else:
    #     listing = Listing.objects.get(pk=listing_id)
    #     if request.user.watchlist.filter(pk=listing_id).exists():
    #         return render(request, "auctions/listing.html", {
    #             "listing_presence": True,
    #             "listing": listing
    #         })
    #     else:
    #         return render(request, "auctions/listing.html", {
    #             "listing_presence": False,
    #             "listing": listing
    #         })



@login_required
def listing(request, listing_id):
    listing = Listing.objects.filter(pk=listing_id).first()

    is_owner = True if listing.owner == request.user else False

    comment_form = CommentForm()

    listing_presence = request.user.watchlist.filter(pk=listing_id).exists()

    Listing_category = Categories.objects.filter(category=listing.category_name).first()

    watchlist_count = request.user.watchlist.all().count()

    latest_bid = Bid.objects.filter(target_listing=listing).order_by("-bid_date").first()

    comments = list(Comment.objects.filter(listing_id=listing_id).order_by("-comment_date"))
    print(comments)
    if latest_bid.bidder == request.user:
        is_bidder = True
    else:
        is_bidder = False
    bid_count = Bid.objects.filter(target_listing=listing).count()

    if request.method == "POST":
        form = BidForm(request.POST)
        if not form.is_valid():
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "listing_presence": listing_presence,
                "watchlist_count": watchlist_count,
                "latest_bid": latest_bid,
                "is_bidder": is_bidder,
                "bid_count": bid_count,
                "listing_category": Listing_category,
                "form": form,
                "comment_form": comment_form,
                "comments": comments,
                "is_owner": is_owner
            })
        bid = form.save(commit=False)
        bid.target_listing = listing
        bid.bidder = request.user
        if not bid.is_valid_bid(listing):
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "listing_presence": listing_presence,
                "watchlist_count": watchlist_count,
                "latest_bid": latest_bid,
                "is_bidder": is_bidder,
                "bid_count": bid_count,
                "listing_category": Listing_category,
                "form": form,
                "invalid_bid": True,
                "comment_form": comment_form,
                "comments": comments,
                "is_owner": is_owner
            })
        bid.save()
        
           
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    else:
        if listing:
            form = BidForm()
            print("listing:", listing)
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "listing_presence": listing_presence,
                "watchlist_count": watchlist_count,
                "latest_bid": latest_bid,
                "is_bidder": is_bidder,
                "bid_count": bid_count,
                "listing_category": Listing_category,
                "form": form,
                "comment_form": comment_form,
                "comments": comments,
                "is_owner": is_owner
            })
        else:
            return render(request, "auctions/error.html", {
                "code": 404,
                "message": "not found"
            })


@login_required
def add_listing(request):
    if request.method == "POST":
        if request.FILES:
            form = ListingForm(request.POST, request.FILES)
        elif request.POST["image_URL"]:
            form = ListingForm(request.POST)
        else:
            form = ListingForm(request.POST)
       
        print("request.POST:", request.POST)
        print("request.FILES:", request.FILES)
        # is form valid?
        if not form.is_valid():
            return render(request, "auctions/add_listing.html", {
                "form": form,
                "watchlist_count": request.user.watchlist.all().count()
            })
        #save to database, w/owner
        listing = form.save(commit=False)
        listing.owner = request.user

        # Fallback to default image if neither ImageField nor URLField given
        if not listing.image_path and not listing.image_URL:
            listing.image_path = "error.png"

        listing.save()
        Bid.objects.create(target_listing=listing, bidder=request.user, first_bid=listing.first_price, current_bid=listing.first_price)
        print(f"Image path: {os.path.join(settings.MEDIA_ROOT, listing.image_path.name)}")
        return HttpResponseRedirect(reverse("index"))
    else:
        listing_form = ListingForm()
        return render(request, "auctions/add_listing.html", {
            "form": listing_form,
            "watchlist_count": request.user.watchlist.all().count()
        })
    
@login_required
def close_listing(request, listing_id):
    listing = Listing.objects.filter(pk=listing_id).first()

    is_owner = True if listing.owner == request.user else False

    comment_form = CommentForm()

    listing_presence = request.user.watchlist.filter(pk=listing_id).exists()

    Listing_category = Categories.objects.filter(category=listing.category_name).first()

    watchlist_count = request.user.watchlist.all().count()

    latest_bid = Bid.objects.filter(target_listing=listing).order_by("-bid_date").first()

    comments = list(Comment.objects.filter(listing_id=listing_id).order_by("-comment_date"))

    listing = Listing.objects.filter(pk=listing_id).first()

    if latest_bid.bidder == request.user:
        is_bidder = True
    else:
        is_bidder = False
    bid_count = Bid.objects.filter(target_listing=listing).count()

    if not listing:
        return HttpResponseRedirect(reverse("error"))
    if request.method == "POST":
        if listing.owner == request.user:
            listing.active = False
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/error.html", {
                "listing": listing,
                "listing_presence": listing_presence,
                "watchlist_count": watchlist_count,
                "latest_bid": latest_bid,
                "is_bidder": is_bidder,
                "bid_count": bid_count,
                "listing_category": Listing_category,
                "comment_form": comment_form,
                "comments": comments,
                "is_owner": is_owner
            })

@login_required
def add_comments(request, listing_id):
    listing = Listing.objects.filter(pk=listing_id).first()

    comment_form = CommentForm()

    listing_presence = request.user.watchlist.filter(pk=listing_id).exists()

    Listing_category = Categories.objects.filter(category=listing.category_name).first()

    watchlist_count = request.user.watchlist.all().count()

    latest_bid = Bid.objects.filter(target_listing=listing).order_by("-bid_date").first()

    if latest_bid.bidder == request.user:
        is_bidder = True
    else:
        is_bidder = False
    bid_count = Bid.objects.filter(target_listing=listing).count()

    if request.method == "POST":
        form = CommentForm(request.POST)
        print("comment:", request.POST)
        if not form.is_valid():
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "listing_presence": listing_presence,
                "watchlist_count": watchlist_count,
                "latest_bid": latest_bid,
                "is_bidder": is_bidder,
                "bid_count": bid_count,
                "listing_category": Listing_category,
                "form": form,
                "invalid_bid": True,
                "comment_form": comment_form
            })
        comment = form.save(commit=False)
        comment.listing_id = listing
        comment.writer = request.user
        print(listing)
        print(request.user)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def categories(request):
    categories = Categories.objects.all()
    for cat in categories:
        print(cat.category)
        print(type(cat.category))
    cat_count = {category.category: Listing.objects.filter(category_name=category).count() for category in categories}
    print(cat_count)
    return render(request, "auctions/categories.html", {
        "watchlist_count": request.user.watchlist.all().count(),
        "categories": categories,
        "cat_count": cat_count
    })

@login_required
def category(request, category_name):
    category = Categories.objects.filter(category=category_name).first()
    category_items = Listing.objects.filter(category_name=category)
    latest_bids = []
    for listing in category_items:
        latest_bid = Bid.objects.filter(target_listing=listing).order_by("-bid_date").first()
        latest_bids.append(latest_bid)
    print(category_name)
    print(category_items)
    return render(request, "auctions/category.html", {
        "watchlist_count": request.user.watchlist.all().count(),
        "category_name": category_name,
        "listings": category_items,
        "latest_bids": latest_bids,
    })

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

def error(request):
    return render(request, "auctions/error.html")