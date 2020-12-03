from django.shortcuts import render

from django.http import JsonResponse

import json

import datetime

from .models import *

# Create your views here.

def store(request):
    context = {}

    # used to show the number of items
    # next to the cart image
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
        total_quantity = order.total_quantity
    else:
        orderitems = []

        # the html will be expecting a variable called order
        # initialize a dictionary with the expected keys
        # which will be viewed as an object
        # with attributes corresponding to the keys
        order = {'total_quantity': 0, 'total_price': 0, 'shipping': False}
        total_quantity = order['total_quantity']

    products = Product.objects.all()

    context['products'] = products
    context['total_quantity'] = total_quantity

    return render(request, 'store/store.html', context=context)


def cart(request):
    context = {}

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
        total_quantity = order.total_quantity
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        print('Cart:', cart)

        orderitems = []

        # the html will be expecting a variable called order
        # initialize a dictionary with the expected keys
        # which will be viewed as an object
        # with attributes corresponding to the keys
        order = {'total_quantity': 0, 'total_price': 0, 'shipping': False}
        total_quantity = order['total_quantity']

        for i in cart:
            try:
                current_quantity = cart[i]['quantity']
                total_quantity += current_quantity

                product = Product.objects.get(id=i)
                total_price = (product.price * current_quantity)

                order['total_price'] += total_price

                orderitem = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'imageURL': product.imageURL
                    },
                    'quantity': current_quantity,
                    'total': total_price
                }
                orderitems.append(orderitem)

                if product.digital == False:
                    order['shipping'] = True
            except:
                pass

    context['orderitems'] = orderitems
    context['order'] = order
    context['total_quantity'] = total_quantity

    return render(request, 'store/cart.html', context=context)


def checkout(request):
    context = {}

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
        total_quantity = order.total_quantity
    else:
        orderitems = []

        # the html will be expecting a variable called order
        # initialize a dictionary with the expected keys
        # which will be viewed as an object
        # with attributes corresponding to the keys
        order = {'total_price': 0, 'total_quantity': 0, 'shipping': False}
        total_quantity = order['total_quantity']

    context['orderitems'] = orderitems
    context['order'] = order
    context['total_quantity'] = total_quantity

    return render(request, 'store/checkout.html', context=context)

def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    print('action: ', action)
    print('product_id: ', product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderitem.quantity += 1
    elif action == 'remove':
        orderitem.quantity -= 1

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()

    return JsonResponse('Item was added.', safe=False)

def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        # validate against actual price from the Order model
        # also check if cart is empty
        if (total == order.total_price) and (len(order.orderitem_set.all()) > 0):
            order.complete = True
        order.save()

        # validate against actual shipping value
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                zipcode=data['shipping']['zipcode']
            )
    else:
        print('User is not logged in.')

    return JsonResponse('Payment complete.', safe=False)