from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import decimal

from .models import User, Bid, Category, Comment, Listing, Auctioned_Items

def index(request):
    if request.method == "POST":
        listing_name = request.POST["searchListing"]
        return render(request, "auctions/index.html", {
            "header_message": "Active Listings",
            "listings": Listing.objects.filter(availability=True, item_name__startswith=listing_name),
            "bids": Bid.objects.filter(is_maximum=True),
            "message": "Unfortunately, there is no active listing with the specified name.",
            "title": "Active Listings"
        })

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
    if request.method == "POST" and 'tos' in request.POST:
        return HttpResponseRedirect(reverse('ToS'))
    elif request.method == "POST":
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
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "auctions/register.html")

def tos_view(request):
    return render(request, "auctions/termsandconditions.html")

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
                bid_amount = decimal.Decimal(request.POST["bid_placement"])
                if bid_amount > current_bid.value:
                    #SET NEW HIGHEST BID
                    Bid.objects.filter(listing=current_listing).update(is_maximum=False)
                    new_current_bid = Bid(value=bid_amount, bidder=request.user, listing=current_listing, is_maximum=True)
                    new_current_bid.save()

                    current_listing.watchlist.add(request.user)
                    current_listing.save()
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
    if request.method == "POST":
        search = request.POST["search_category"]

        return render(request, "auctions/categories.html", {
            'category_list': Category.objects.all().filter(category_name__startswith=search)
        })

    return render(request, "auctions/categories.html", {
        'category_list': Category.objects.all()
    })

@login_required(login_url='/login')
def own_listings(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all().filter(item_lister=request.user),
        'header_message': f"{request.user}'s Listings",
        'bids': Bid.objects.filter(is_maximum=True),
        "message": "You have no active listings.",
        "title": "My Listings"
    })

@login_required(login_url='/login')
def filtered_view(request, category_id):
    category = Category.objects.get(id=category_id)
    available_listings = Listing.objects.all().filter(item_category=category_id, availability=True)

    error_message = ""
    if available_listings.count() == 0:
        error_message = "Unfortunately, there are no listings of this category available."

    return render(request, "auctions/index.html", {
        'listings': available_listings,
        'header_message': f"Category: {category.category_name}",
        'bids': Bid.objects.filter(is_maximum=True),
        'title': f"{category.category_name}",
        "no_listings": error_message
    })

@login_required(login_url='/login')
def create(request):
    if request.method == "POST":
        item_name = request.POST["item_name"]
        description = request.POST["description"]
        img_file = request.FILES["img_file"]
        starting_price = decimal.Decimal(request.POST["starting_price"])
        category = request.POST["category_choice"]

        #IF ALL FIELDS WERE FILLED OUT
        if item_name != "" and description != "" and starting_price != "":
            if img_file != "" and category != "":
                chosen_category = Category.objects.get(category_name=category)
                new_listing = Listing(item_name=item_name, description=description, image_file=img_file,
                                      availability=True,
                                      item_lister=request.user, item_category=chosen_category)
                new_listing.save()
                new_starting_bid = Bid(value=decimal.Decimal(starting_price), bidder=request.user, listing=new_listing, is_maximum=True)
                new_starting_bid.save()
                return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))

            #IF ALL FIELDS EXCEPT IMAGE LINK WERE FILLED OUT
            elif category != "":
                chosen_category = Category.objects.get(category_name=category)
                new_listing = Listing(item_name=item_name, description=description, availability=True,
                                      item_lister=request.user, item_category=chosen_category)
                new_listing.save()
                new_starting_bid = Bid(value=decimal.Decimal(starting_price), bidder=request.user, listing=new_listing, is_maximum=True)
                new_starting_bid.save()
                return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))

            # IF ALL FIELDS EXCEPT IMAGE LINK AND CATEGORY WERE FILLED OUT
            else:
                new_listing = Listing(item_name=item_name, description=description, availability=True,
                                          item_lister=request.user)
                new_listing.save()
                new_starting_bid = Bid(value=decimal.Decimal(starting_price), bidder=request.user, listing=new_listing, is_maximum=True)
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
    if request.method == "POST":
        listing_name = request.POST["searchListing"]
        return render(request, "auctions/index.html", {
            "listings": Listing.objects.filter(watchlist=request.user, item_name__startswith=listing_name),
            'header_message': f"{request.user}'s Watchlist",
            'bids': Bid.objects.filter(is_maximum=True),
            "message": "You have no active listings in your watchlist.",
            "title": "Watchlist"
        })

    return render(request, "auctions/index.html", {
        'listings': Listing.objects.all().filter(watchlist=request.user),
        'header_message': f"{request.user}'s Watchlist",
        'bids': Bid.objects.filter(is_maximum=True),
        "message": "You have no active listings in your watchlist.",
        "title": "Watchlist"
    })

@login_required(login_url='/login')
def email_view(request, item_name):
    if request.method == "POST":
        full_name = request.POST["fullname"]
        address = request.POST["address"]
        contact = request.POST["contact"]

        ##VERIFY USER
        listing = Listing.objects.get(item_name=item_name)
        verify = Bid.objects.get(listing=listing, bidder=request.user, is_maximum=True)

        if verify is not None:
            #SEND EMAIL TO GOOGLE
            subject = f'Auction Winner: {full_name} ({request.user.username})'
            message = f'Good day! We are notifying you about the details of the user that won your auction {listing.item_name}.\n' \
                f'Please contact the user through the e-mail address and contact numbers they have provided.\n' \
                f'\n-----------------------------------------------------------\n'\
                f'DETAILS:\nE-mail: {request.user.email}\nContact Number: {contact}\nAddress: {address}'

            email_from = settings.EMAIL_HOST_USER
            recipient_list = [listing.item_lister.email]
            send_mail(subject, message, email_from, recipient_list)

            auctioned_item = Auctioned_Items(auctioned_item=listing, new_owner=verify)
            auctioned_item.save()
            return HttpResponseRedirect(reverse(index))
        else:
            return HttpResponseRedirect("It seems you are not the winner of this auction...")

    return render(request, "auctions/winnerdetails.html")