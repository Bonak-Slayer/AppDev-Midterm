from django.shortcuts import render
from decimal import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from . models import User, Product, Cart, Cart_Item, Shipping, Shipping_Details, Job_Order, Job_Items

# Create your views here.
def index(request):
    #STORE THE CURRENT NAME OF THE PAGE
    if "origin" not in request.session:
        request.session["origin"] = "homepage"
    # IF THE CUSTOMER IS ACCESSING THE PAGE AND HAS NO CART
    if "cart_id" not in request.session:
        provide_cart = Cart(customer=None)
        provide_cart.save()
        request.session["cart_id"] = provide_cart.id

    request.session["origin"] = "homepage"
    return render(request, "shoppingcart/homepage.html", {
        "items": Product.objects.all()
    })

def login_view(request):
    #IF THE USER IMMEDIATELY ACCESSES THE PAGE
    if "origin" not in request.session:
        request.session["origin"] = "homepage"
    # IF THE CUSTOMER IS ACCESSING THE PAGE AND HAS NO CART
    if "cart_id" not in request.session:
        provide_cart = Cart(customer=None)
        provide_cart.save()
        request.session["cart_id"] = provide_cart.id

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            access = User.objects.get(email=email)
        except:
            return render(request, "shoppingcart/login.html", {
                "error_message": "*No such user.",
                "submit_message": "Log In",
                "register_offer": "Don't have an account? Register here."
            })

        user = authenticate(request, username=access.username, password=password)
        if user is not None:
            #IF THE USER LOGGED IN, THEN SET THE CURRENT CART'S CUSTOMER TO THE USER'S NAME
            cart_verified = Cart.objects.get(id=request.session["cart_id"])
            cart_verified.customer = user
            login(request, user)
            origin = request.session["origin"]
            # CHECK WHERE THE USER HAS LAST BEEN LOCATED BEFORE LOGGING IN
            if origin == "homepage":
                return HttpResponseRedirect(reverse("Shop:index"))
            elif origin == "cart":
                return HttpResponseRedirect(reverse("Shop:cart"))
            elif origin == "checkout":
                return HttpResponseRedirect(reverse("Shop:shipping"))

    return render(request, "shoppingcart/login.html", {
        "message": "Log In",
        "submit_message": "Log In",
        "register_offer": "Don't have an account? Register here."
    })

def register_view(request):
    # IF THE CUSTOMER IS ACCESSING THE PAGE AND HAS NO CART
    if "cart_id" not in request.session:
        provide_cart = Cart(customer=None)
        provide_cart.save()
        request.session["cart_id"] = provide_cart.id

    if request.method == "POST":
        email = request.POST["email"]
        try:
            check_existing = User.objects.get(email=email)
        except:
            #IF PASSWORDS MATCH
            if request.POST["password"] == request.POST["confirmation"]:
                username = request.POST["firstname"]

                password = request.POST["password"]
                first_name = username
                last_name = request.POST["lastname"]

                new_user = User.objects.create_user(username, email, password)
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.save()

                login(request, new_user)
                origin = request.session["origin"]
                #CHECK WHERE THE USER HAS LAST BEEN LOCATED BEFORE REGISTERING
                if origin == "homepage":
                    return HttpResponseRedirect(reverse("Shop:index"))
                elif origin == "cart":
                    return HttpResponseRedirect(reverse("Shop:cart"))
                elif origin == "checkout":
                    return HttpResponseRedirect(reverse("Shop:shipping"))
            #IF PASSWORDS DO NOT MATCH
            else:
                return render(request, "shoppingcart/register.html", {
                    "message": "Register",
                    "submit_message": "Finish",
                    "pass_error": "*Passwords do not match."
                })
        #IF THERE IS AN EXISTING ACCOUNT, REJECT REGISTRATION
        if check_existing is not None:
            return render(request, "shoppingcart/register.html", {
                "message": "Register",
                "submit_message": "Finish",
                "email_error": "*This e-mail is already taken."
            })

    return render(request, "shoppingcart/register.html", {
        "message": "Register",
        "submit_message": "Finish"
    })

@login_required(login_url="Shop:login")
def logout_view(request):
    #DELETE TRASHED VALUES
    current_cart = Cart.objects.get(id=request.session["cart_id"])
    Cart_Item.objects.all().filter(cart=current_cart).delete()
    current_cart.delete()

    #CLEAR SESSION VARIABLES
    request.session.flush()
    logout(request)
    return HttpResponseRedirect(reverse("Shop:index"))


def product_view(request, product_id):
    #IF THE CUSTOMER IS ACCESSING THE PAGE AND HAS NO CART
    if "cart_id" not in request.session:
        provide_cart = Cart(customer=None)
        provide_cart.save()
        request.session["cart_id"] = provide_cart.id

    #CHECK IF PRODUCT EXISTS, IF NOT, THEN RETURN ERROR PAGE
    try:
        product = Product.objects.get(id=product_id)
    except:
        return HttpResponseNotFound('<h1>NO SUCH PAGE. BRUH.</h1>')

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 0))
        current_cart = Cart.objects.get(id=request.session["cart_id"])
        #CHECK IF THERE IS A SIMILAR PRODUCT IN THE CART
        try:
            check_similar_product = Cart_Item.objects.get(cart=current_cart, product=product)
            check_similar_product.quantity += quantity
            check_similar_product.save()
        except:
            new_cart_item = Cart_Item(cart=current_cart, product=product, quantity=quantity)
            new_cart_item.save()

        return HttpResponseRedirect(reverse("Shop:cart"))

    request.session["origin"] = "checkout"
    return render(request, "shoppingcart/product_details.html", {
        "page_title": product.product_name,
        "product_name": product.product_name,
        "product_image": product.img_url,
        "price": product.price,
        "description": product.description,
        "stock": product.stock
    })

def cart_view(request):
    # STORE THE CURRENT NAME OF THE PAGE
    if "origin" not in request.session:
        request.session["origin"] = "checkout"
    # IF THE CUSTOMER IS ACCESSING THE PAGE AND HAS NO CART
    if "cart_id" not in request.session:
        provide_cart = Cart(customer=None)
        provide_cart.save()
        request.session["cart_id"] = provide_cart.id
    #SETTING GENERAL VARIABLE
    cart_items = Cart_Item.objects.all().filter(cart=request.session["cart_id"])

    #GETTING INDIVIDUAL VALUES FROM THE VARIOUS ENTRIES IN THE CART PAGE
    if request.method == "POST":
        #IF THE USER WANTS TO CHECK OUT
        if "checkout" in request.POST:
            request.session["origin"] = "checkout"
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse("Shop:shipping"))
            else:
                return HttpResponseRedirect(reverse("Shop:login"))
        #IF THE USER WANTS TO UPDATE ITEMS IN THEIR CART
        else:
            current_cart = Cart.objects.get(id=request.session["cart_id"])
            cart_item_id = int(request.POST.get("cart_item_id", 0))
            quantity = int(request.POST.get(f"update{cart_item_id}", 0))
            product_name = request.POST[f"product_name{cart_item_id}"]

            product = Product.objects.get(product_name=product_name)
            updated_cart_item = Cart_Item.objects.get(product=product, cart=current_cart)
            updated_cart_item.quantity = quantity
            updated_cart_item.save()

            return HttpResponseRedirect(reverse("Shop:cart"))

        #### CALCULATION OF SUBTOTAL, EXTRACTION OF SHIPPING FEE AND COMPUTATION OF GRAND TOTAL ###
    subtotal = 0
    total_weight = 0
    remaining_weight = 0
    shipping_fee = 0
    #SUBTOTAL
    for cart_item in cart_items:
        subtotal += cart_item.quantity * cart_item.product.price
        total_weight += cart_item.quantity * cart_item.product.weight

    #EXTRACT MAX SHIPPING FEE
    shipping_last_type = Shipping.objects.aggregate(max_weight=Max('max_weight'))
    max_shipping_weight = shipping_last_type.get('max_weight')

    #IF THE TOTAL WEIGHT IS GREATER THAN ALL OPTIONS FOR SHIPPING
    if total_weight > max_shipping_weight:
        remaining_weight += total_weight
        max_shipping_price = Shipping.objects.get(max_weight=max_shipping_weight)

        ##AS LONG AS THE TOTAL WEIGHT IS LARGER THAN THE MAXIMUM SHIPPING WEIGHT, DEDICATE A\
        ##NEW, SEPARATE SHIPPING TO THE ITEMS AND RECORD THE REDUCED TOTAL WEIGHT SO THAT
        ##THE SYSTEM CAN ASSIGN A PROPER SHIPPING TYPE
        while(remaining_weight > max_shipping_weight):
            shipping_fee += max_shipping_price.price
            remaining_weight = float(remaining_weight) - max_shipping_weight

        #NOW THAT THE REMAINING WEIGHT CAN BE ASSIGNED A SPECIFIC SHIPPING TYPE, DO SO IN THIS SECTION
        if remaining_weight > 0:
            shipping_types = Shipping.objects.all()
            for type in shipping_types:
                if type.min_weight <= remaining_weight and type.max_weight >= remaining_weight:
                    shipping_fee += type.price
    else:
        shipping_types = Shipping.objects.all()
        for type in shipping_types:
            if type.min_weight <= total_weight and type.max_weight >= total_weight:
                shipping_fee = type.price

    # CALCULATE GRAND TOTAL
    VAT = Decimal(subtotal * Decimal(.12)).quantize(Decimal('.01'), rounding=ROUND_UP)
    grand_total = VAT + subtotal + Decimal(shipping_fee).quantize(Decimal('.01'), rounding=ROUND_UP)

    #STORING REUSABLE VARIABLES IN SESSION
    request.session["origin"] = "cart"
    request.session["total_weight"] = float(total_weight)
    request.session["subtotal"] = float(subtotal)
    request.session["shipping_fee"] = shipping_fee
    request.session["grand_total"] = float(grand_total)
    request.session['remaining_weight'] = remaining_weight

    return render(request, "shoppingcart/cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_fee": request.session["shipping_fee"],
        "grand_total":grand_total,
        "total_weight": total_weight
    })

def delete_item(request, item_name):
    #GET THE ID OF THE PRODUCT TO BE REMOVED FROM THE CART AND DELETE IT
    remove_product = Product.objects.get(product_name=item_name)
    carted_products = Cart_Item.objects.all().filter(cart=request.session["cart_id"])
    for product in carted_products:
        if product.product_id == remove_product.id:
            product.delete()
    #REDIRECT TO CART PAGE
    request.session["origin"] = "cart"
    return HttpResponseRedirect(reverse("Shop:cart"))

@login_required(login_url="Shop:login")
def shipping_view(request):
    def new_shipping(shipping_type):
        # IF BOTH ADDRESSES ARE FILLED
        if address2 != "" and address3 != "":
            new_shipping = Shipping_Details(shipping_type=shipping_type, shipment_owner=user, address1=address1,
                                            address2=address2, full_name=fullname,
                                            address3=address3, city=city, state=state, country=country)
            new_shipping.save()
        # WHEN ONLY THE 2ND ADDRESS IS FILLED
        elif address2 != "":
            new_shipping = Shipping_Details(shipping_type=shipping_type, shipment_owner=user, address1=address1,
                                            full_name=fullname, address2=address2, city=city, state=state,
                                            country=country)
            new_shipping.save()
        # IF ADDRESS 2 AND ADDRESS 3 ARE BLANK
        elif address2 == "" and address3 == "":
            new_shipping = Shipping_Details(shipping_type=shipping_type, shipment_owner=user, address1=address1,
                                            full_name=fullname, city=city, state=state, country=country)
            new_shipping.save()
        # IF USER TRIES TO FILL OUT THE 3RD ADDRESS IMMEDIATELY
        elif address2 == "" and address3 != "":
            return render(request, "shoppingcart/shipping.html", {
                "error_message": "Please fill out the required fields.",
                "name_error": "*Required",
                "address_error": "*Please fill out the 2nd address before filling out the 3rd one.",
                "city_error": "*Required",
                "state_error": "*Required",
                "country_error": "*Required"
            })

    total_weight = request.session["total_weight"]

    if request.method == "POST":
        fullname = request.POST["full-name"]
        address1 = request.POST["address1"]
        address2 = request.POST["address2"]
        address3 = request.POST["address3"]
        city = request.POST["city"]
        state = request.POST["state"]
        country = request.POST["country"]

        shipping_types = Shipping.objects.all()
        remaining_weight = 0
        user = request.user
        if fullname != "" and address1 != "" and city != "" and state != "" and country != "":
            #ASSIGN MAXIMUM SHIPPING PRICE TO A VARIABLE
            shipping_last_type = Shipping.objects.aggregate(max_weight=Max('max_weight'))
            max_shipping_weight = shipping_last_type.get('max_weight')

            # IF THE TOTAL WEIGHT IS GREATER THAN ALL OPTIONS FOR SHIPPING
            if total_weight > max_shipping_weight:
                remaining_weight += total_weight
                max_shipping_price = Shipping.objects.get(max_weight=max_shipping_weight)

                ##AS LONG AS THE TOTAL WEIGHT IS LARGER THAN THE MAXIMUM SHIPPING WEIGHT, DEDICATE A\
                ##NEW, SEPARATE SHIPPING TO THE ITEMS AND RECORD THE REDUCED TOTAL WEIGHT SO THAT
                ##THE SYSTEM CAN ASSIGN A PROPER SHIPPING TYPE
                while (remaining_weight > max_shipping_weight):
                    new_shipping(max_shipping_price)
                    remaining_weight = float(remaining_weight) - max_shipping_weight

                # NOW THAT THE REMAINING WEIGHT CAN BE ASSIGNED A SPECIFIC SHIPPING TYPE, DO SO IN THIS SECTION
                if remaining_weight > 0:
                    for type in shipping_types:
                        if type.min_weight <= remaining_weight and type.max_weight >= remaining_weight:
                            new_shipping(type)
            else:
                for type in shipping_types:
                    if type.min_weight <= total_weight and type.max_weight >= total_weight:
                        new_shipping(type)

            return HttpResponseRedirect(reverse("Shop:payment"))
        else:
            return render(request, "shoppingcart/shipping.html", {
                "error_message": "Please fill out the required fields.",
                "name_error": "*Required",
                "address_error": "*Required",
                "city_error": "*Required",
                "state_error": "*Required",
                "country_error": "*Required"
            })

    error_message = ''
    if total_weight < float(1):
        error_message = "The minimum weight for a shipment is 1kg."
    return render(request, "shoppingcart/shipping.html", {
        "error_message": error_message
    })

@login_required(login_url="Shop:login")
def payment_view(request):
    cart_items = Cart_Item.objects.all().filter(cart=request.session["cart_id"])
    if request.method == "POST":
        #CREATE NEW ORDER
        shipping_details = Shipping_Details.objects.filter(shipment_owner=request.user).aggregate(max_id=Max('pk'))
        exact = Shipping_Details.objects.get(id=shipping_details.get('max_id'))
        new_order = Job_Order(customer=request.user, shipping_details=exact)
        new_order.save()
        request.session["job_order_id"] = new_order.id
        #TRANSFER CART DATA INTO JOB ITEMS
        for item in cart_items:
            order_item = Job_Items(order_id=new_order, product=item.product, quantity=item.quantity)
            order_item.save()
            #REDUCE STOCK
            product = Product.objects.get(id=item.product.id)
            product.stock -= item.quantity
            product.save()

        return HttpResponseRedirect(reverse("Shop:confirmation"))

    return render(request, "shoppingcart/payment.html", {
        "payment_items": cart_items,
        "total_weight": request.session["total_weight"],
        "subtotal": request.session["subtotal"],
        "shipping_fee": request.session["shipping_fee"],
        "grand_total": request.session["grand_total"]
    })

@login_required(login_url="Shop:login")
def confirmation_view(request):
    if request.method == "POST":
        current_cart = Cart.objects.get(id=request.session["cart_id"])
        Cart_Item.objects.all().filter(cart=current_cart).delete()
        current_cart.delete()

        #CREATE NEW CART FOR CUSTOMER
        provide_cart = Cart(customer=None)
        provide_cart.save()
        request.session["cart_id"] = provide_cart.id
        return HttpResponseRedirect(reverse("Shop:index"))

    #EXTRACT DATA FOR TEMPLATE
    job_id = request.session["job_order_id"]
    shipping_details = Shipping_Details.objects.filter(shipment_owner=request.user).aggregate(max_id=Max('pk'))
    exact = Shipping_Details.objects.get(id=shipping_details.get('max_id'))

    return render(request, "shoppingcart/confirmation.html", {
        "confirmation_items": Job_Items.objects.all().filter(order_id=job_id),
        "total_weight": request.session["total_weight"],
        "subtotal": request.session["subtotal"],
        "shipping_fee": request.session["shipping_fee"],
        "grand_total": request.session["grand_total"],
        "full_name": exact.full_name,
        "address_3": exact.address3,
        "city": exact.city,
        "state": exact.state,
        "country": exact.country,
        "address_1": exact.address1,
        "address_2": exact.address2,
    })