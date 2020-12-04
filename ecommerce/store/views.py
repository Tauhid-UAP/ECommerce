from django.shortcuts import render

from django.http import JsonResponse

import json

import datetime

from .models import *

from .utils import *

# Create your views here.

def store(request):
    context = {}

    data = cart_data(request)

    products = Product.objects.all()

    context['products'] = products
    context['total_quantity'] = data['total_quantity']

    return render(request, 'store/store.html', context=context)


def cart(request):
    context = cart_data(request)

    return render(request, 'store/cart.html', context=context)


def checkout(request):
    context = cart_data(request)

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