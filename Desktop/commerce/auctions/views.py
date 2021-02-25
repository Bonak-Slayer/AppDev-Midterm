from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Bid, Category, Comment, Listing


def index(request):
    return render(request, "auctions/index.html", {
        "header_message": "Active Listings",
        "listings": Listing.objects.filter(availability=True),
        "bids": Bid.objects.filter(is_maximum=True),
        "message": "Sorry, there are currently no active listings.",
        "title": "Active Listings"
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
            return render(request, "auctions/index.html", {
                "header_message": "Active Listings",
                "listings": Listing.objects.filter(availability=True),
                "bids": Bid.objects.filter(is_maximum=True),
                "message": "Sorry, there are currently no active listings.",
                "title": "Active Listings"
            })
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return render(request, "auctions/index.html", {
        "header_message": "Active Listings",
        "listings": Listing.objects.filter(availability=True),
        "bids": Bid.objects.filter(is_maximum=True),
        "message": "Sorry, there are currently no active listings.",
        "title": "Active Listings"
    })


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
        return render(request, "auctions/index.html", {
            "header_message": "Active Listings",
            "listings": Listing.objects.filter(availability=True),
            "bids": Bid.objects.filter(is_maximum=True),
            "message": "Sorry, there are currently no active listings.",
            "title": "Active Listings"
        })
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def listing_view(request, listing_id):
    try:
        current_listing = Listing.objects.get(pk=listing_id)
    except:
        return render(request, "auctions/index.html", {
            "header_message": "This listing does not exist.",
            "title": "Listing Not Found"
        })

    current_bid = Bid.objects.get(listing=current_listing, is_maximum=True)

    #BIDDING FEATURE
    if request.method == "POST":
        if "bid_placement" in request.POST and current_listing.availability == True:
            if request.POST["bid_placement"] != "":
                bid_amount = int(request.POST["bid_placement"])
                if bid_amount > current_bid.value:
                    Bid.objects.filter(listing=current_listing).update(is_maximum=False)
                    new_current_bid = Bid(value=bid_amount, bidder=request.user, listing=current_listing, is_maximum=True)
                    new_current_bid.save()
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": Listing.objects.get(pk=listing_id),
                        "comments": Comment.objects.all().filter(listing=listing_id),
                        "bid_count": Bid.objects.all().filter(listing=listing_id).count(),
                        "bid_value": current_bid.value,
                        "bidder": current_bid.bidder,
                        "message": "Sorry, your bid was invalid. Bids need to be higher than the current bid."
                    })
        #COMMENT FEATURE
        elif "comment" in request.POST:
            if request.POST["comment"] != "":
                text = request.POST["comment"]
                current_listing = Listing.objects.get(pk=listing_id)
                new_comment = Comment(text=text, commenter=request.user, listing=current_listing)
                new_comment.save()

        #WATCHLIST FEATURE
        elif "watchlist_interaction" in request.POST:
            if request.user in current_listing.watchlist.all():
                current_listing.watchlist.remove(request.user)
            else:
                current_listing.watchlist.add(request.user)
                current_listing.save()
        elif "close_auction" in request.POST:
            auction_winner = current_bid.bidder
            current_listing.watchlist.add(auction_winner)
            current_listing.availability = False
            current_listing.save()

    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(pk=listing_id),
        "comments": Comment.objects.all().filter(listing=listing_id),
        "bid_count": Bid.objects.all().filter(listing=listing_id).count(),
        "bid_value": current_bid.value,
        "bidder": current_bid.bidder
    })

@login_required(login_url='/login')
def categories(request):
    return render(request, "auctions/categories.html", {
        'category_list': Category.objects.all()
    })

@login_required(login_url='/login')
def filtered_view(request, category_id):
    category = Category.objects.get(id=category_id)

    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all().filter(item_category=category_id, availability=True),
        'header_message': f"Category: {category.category_name}",
        'bids': Bid.objects.filter(is_maximum=True),
        'title': f"{category.category_name}"
    })

@login_required(login_url='/login')
def create(request):
    if request.method == "POST":
        item_name = request.POST["item_name"]
        description = request.POST["description"]
        img_url = request.POST["img_url"]
        starting_price = request.POST["starting_price"]
        category = request.POST["category_choice"]

        #IF ALL FIELDS WERE FILLED OUT
        if item_name != "" and description != "" and starting_price != "":
            if img_url != "" and category != "":
                chosen_category = Category.objects.get(category_name=category)
                new_listing = Listing(item_name=item_name, description=description, image_link=img_url,
                                      availability=True,
                                      item_lister=request.user, item_category=chosen_category)
                new_listing.save()
                new_starting_bid = Bid(value=int(starting_price), bidder=request.user, listing=new_listing, is_maximum=True)
                new_starting_bid.save()
                return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))

            #IF ALL FIELDS EXCEPT THE CATEGORY WERE FILLED OUT
            elif img_url != "":
                new_listing = Listing(item_name=item_name, description=description, image_link=img_url, availability=True,
                                      item_lister=request.user)
                new_listing.save()
                new_starting_bid = Bid(value=int(starting_price), bidder=request.user, listing=new_listing, is_maximum=True)
                new_starting_bid.save()
                return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))

            #IF ALL FIELDS EXCEPT IMAGE LINK WERE FILLED OUT
            elif category != "":
                chosen_category = Category.objects.get(category_name=category)
                new_listing = Listing(item_name=item_name, description=description, availability=True,
                                      item_lister=request.user, item_category=chosen_category)
                new_listing.save()
                new_starting_bid = Bid(value=int(starting_price), bidder=request.user, listing=new_listing, is_maximum=True)
                new_starting_bid.save()
                return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))

            # IF ALL FIELDS EXCEPT IMAGE LINK AND CATEGORY WERE FILLED OUT
            else:
                new_listing = Listing(item_name=item_name, description=description, availability=True,
                                          item_lister=request.user)
                new_listing.save()
                new_starting_bid = Bid(value=int(starting_price), bidder=request.user, listing=new_listing, is_maximum=True)
                new_starting_bid.save()
                return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))
        else:
            return render(request, "auctions/create.html", {
                "categories": Category.objects.all(),
                "error_message": "Please fill out the required fields.",
                "invalid_submission": True
            })

    return render(request, "auctions/create.html", {
        "categories": Category.objects.all()
    })

@login_required(login_url='/login')
def watchlist(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all().filter(watchlist=request.user),
        'header_message': f"{request.user}'s Watchlist",
        'bids': Bid.objects.filter(is_maximum=True),
        "message": "You have no active listings in your watchlist.",
        "title": "Watchlist"
    })