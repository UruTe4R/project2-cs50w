from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/toggle/<int:listing_id>", views.add_watchlist, name="toggle_watchlist"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("close_listing/<int:listing_id>", views.close_listing, name="close_listing"),
    path("add/comments/<int:listing_id>", views.add_comments, name="add_comments"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_name>", views.category, name="category"),
    path("error", views.error, name="error"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
