from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name="watchlist", blank=True)

    def __str__(self):
        return f"id {self.id} {self.username}"




class Bid(models.Model):
    target_listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='target')

    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bidder', blank=True)

    first_bid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    current_bid = models.DecimalField(max_digits=10, decimal_places=2)

    bid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  f"bidder: {self.bidder}, first_bid: {self.first_bid}, current_bid: {self.current_bid}"
    
    def is_valid_bid(self, listing):
        """
        Validate the bid:
        1. Ensure the bid is positive.
        2. Ensure the bid is greater than the latest bid.
        """
        if self.current_bid <= 0:
            return False

        latest_bid = Bid.objects.filter(target_listing=listing).order_by("-bid_date").first()
        print("latest_bid:", latest_bid.current_bid)
        print("current_bid:", self.current_bid)
        if latest_bid and self.current_bid <= latest_bid.current_bid:
            return False
        return True


class Categories(models.Model):
    category = models.CharField(default="Else", max_length=64, unique=True)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')

    title = models.CharField(max_length=100)

    description = models.TextField(max_length=500)

    image_path = models.ImageField(blank=True)

    image_URL = models.URLField(blank=True)

    # current price should be based on Bid Class
    first_price = models.DecimalField(max_digits=10, decimal_places=2)

    creation_date = models.DateTimeField(auto_now_add=True)

    category_name = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="category_name", null=True)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.owner}"

class Comment(models.Model):
    # who, what comment, when
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writer')

    comment = models.TextField(max_length=500)

    comment_date = models.DateTimeField(auto_now_add=True)

    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_id")

    def __str__(self):
        return f"{self.writer} | {self.comment[:20]}... at {self.comment_date}"

class Reply(models.Model):
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='what_comment')

    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reponder')

    response = models.TextField(max_length=500)

    response_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.comment_id.writer}, {self.responder} '{self.response}'"