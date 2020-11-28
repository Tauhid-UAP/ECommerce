from django.shortcuts import render

from django.http import JsonResponse

import json

from django.views.decorators.csrf import csrf_exempt

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
        orderitems = []

        # the html will be expecting a variable called order
        # initialize a dictionary with the expected keys
        # which will be viewed as an object
        # with attributes corresponding to the keys
        order = {'total_quantity': 0, 'total_price': 0, 'shipping': False}
        total_quantity = order['total_quantity']

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
        order = {'total_quantity': 0, 'total_price': 0, 'shipping': False}
        total_quantity = order['total_quantity']

    context['orderitems'] = orderitems
    context['order'] = order
    context['total_quantity'] = total_quantity

    return render(request, 'store/checkout.html', context=context)

# @ csrf_exempt
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