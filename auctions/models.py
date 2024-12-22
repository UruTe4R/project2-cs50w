from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"id {self.id} {self.username}"




class Bid(models.Model):
    target_listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='target')

    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bidder')

    first_bid = models.DecimalField(max_digits=10, decimal_places=2)

    current_bid = models.DecimalField(max_digits=10, decimal_places=2)

    active = models.BooleanField(default=True)

    bid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"seller: {self.seller}, bidder: {self.bidder}, first_bid: {self.first_bid}, current_bid: {self.current_bid}, active: {self.active}, creation_date: {self.creation_date}"

class Categories(models.Model):
    category = models.CharField(default="Else", max_length=64, unique=True)

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')

    title = models.CharField(max_length=100)

    description = models.TextField(max_length=500)

    photo = models.ImageField(default="error.png", blank=True)

    # current price should be based on Bid Class
    first_price = models.DecimalField(max_digits=10, decimal_places=2)

    creation_date = models.DateTimeField(auto_now_add=True)

    category_name = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="category_name", null=True)

class Comment(models.Model):
    # who, what comment, when
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writer')

    comment = models.TextField(max_length=500)

    comment_date = models.DateTimeField(auto_now_add=True)

class Reply(models.Model):
    what_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='what_comment')

    reponder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reponder')

    response = models.TextField(max_length=500)

    response_date = models.DateTimeField(auto_now_add=True)