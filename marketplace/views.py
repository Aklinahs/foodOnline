from unicodedata import category
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from marketplace.context_processors import get_cart_amounts, get_cart_counter
from marketplace.models import Cart
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from vendor.models import Vendor

# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, 'marketplace/listing.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset= FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        context = {
            'vendor': vendor,
            'categories' : categories,
            'cart_items' : cart_items,
        }
    else:
        context = {
            'vendor': vendor,
            'categories' : categories,
        }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id=None):
    print(request.user.is_authenticated)
    if request.user.is_authenticated :
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'increased', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'added the food', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)  })
            except:
                return JsonResponse({'status': 'Failed', 'message': 'not exixst'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'invalid'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'please logged in'})


def decrease_cart(request, food_id):
    if request.user.is_authenticated :
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'message': 'increased', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'this food does not exist' })
            except:
                return JsonResponse({'status': 'Failed', 'message': 'not exixst'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'invalid'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'please logged in'})

@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context ={
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


@login_required(login_url = 'login')
def delete_cart(request, cart_id):
    if request.user.is_authenticated :
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'deleted', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'nott exixst'}) 
        else:
            return JsonResponse({'status': 'Failed', 'message': 'invalid'})