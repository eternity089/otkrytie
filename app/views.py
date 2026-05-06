from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, F, DecimalField, Q
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic

from .forms import RegisterUserForm
from django.urls import reverse_lazy, reverse
from django.views.generic import DetailView

from .models import Product, Order, Cart, Category, Address, City, ItemInOrder


def about(request):
    breadcrumbs = [
        {'name': 'Главная', 'url': reverse('home')},
        {'name' : 'О компании', 'url': None},
    ]
    return render(request, 'app/about.html', {'breadcrumbs': breadcrumbs})

def register_view(request):
    show_register_modal = False
    form = RegisterUserForm(request.POST)

    if request.method == 'POST':
        next_url = request.POST.get('next', '/')

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(next_url)
        else:
            show_register_modal = True


    return render(request, 'app/home.html', {
        'register_form': form,
        'show_register_modal': show_register_modal
    })

def login_view(request):
    show_login_modal = False
    error_message = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            show_login_modal = True
            error_message = "Неправильный логин или пароль"

    return render(request, 'app/home.html', {
        'show_login_modal': show_login_modal,
        'login_error': error_message
    })

def home(request):
    categories = Category.objects.all()
    products = Product.objects.order_by('-date')[:10]
    return render(request, 'app/home.html', {'categories': categories, 'products': products})

def search(request):
    query = request.GET.get('q', '').strip().lower()
    products = []

    if query:
        products = Product.objects.annotate(
            name_lower=Lower('name'),
            desc_lower=Lower('description')
        ).filter(
            Q(name_lower__contains=query) |
            Q(desc_lower__contains=query)
        )

    return render(request, 'app/search.html', {
        'products': products,
        'query': query
    })

def contact(request):
    breadcrumbs = [
        {'name': 'Главная', 'url': reverse('home')},
        {'name': 'Контакты', 'url': None},
    ]
    return render(request, 'app/contact.html', {'breadcrumbs': breadcrumbs})

def catalog(request, slug):
    if slug == 'sale':
        products = Product.objects.filter(old_price__isnull=False)
        title = 'Акции и скидки'
        breadcrumbs = [
            {'name': 'Главная', 'url': reverse('home')},
            {'name': 'Акции и скидки', 'url': None},
        ]
    else:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category)
        title = category.name
        breadcrumbs = [
            {'name': 'Главная', 'url': reverse('home')},
            {'name': category.name, 'url': None},
        ]
    return render(request, 'app/catalog.html', {
        'products': products,
        'title': title,
        'breadcrumbs' : breadcrumbs,
    })

class ProductDetail(DetailView):
    model = Product
    template_name = 'app/product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['breadcrumbs'] = [
            {'name': 'Главная', 'url': reverse('home')},
            {
                'name': product.category.name,
                'url': reverse('catalog', args=[product.category.slug])
            },
            {'name': product.name, 'url': None},
        ]
        return context

@login_required
def cart(request):
    cart_items = request.user.cart_set.select_related('product')
    cities = City.objects.all()
    city_id = request.session.get('city_id')
    address_id = request.session.get('address_id')
    selected_city = None
    selected_address = None
    addresses = []
    if city_id:
        selected_city = City.objects.filter(id=city_id).first()
        addresses = Address.objects.filter(city_id=city_id)
    if address_id:
        selected_address = Address.objects.filter(id=address_id).first()
    total_price = sum(item.count * item.product.price for item in cart_items)
    if request.method == "POST":
        if not cart_items:
            messages.error(request, 'Корзина пуста')
            return  redirect('cart')
        if not address_id:
            messages.error(request, 'Выберите адрес')
            return redirect('cart')
        order = Order.objects.create(
            user=request.user,
            city_id=city_id if city_id else None,
            address_id=address_id
        )
        for item in cart_items:
            ItemInOrder.objects.create(
                order=order,
                product=item.product,
                count=item.count,
                price=item.count * item.product.price
            )
        cart_items.delete()
        return redirect('orders')
    return render(request, 'app/cart.html', {
        'cart_items': cart_items,
        'cities': cities,
        'selected_city': selected_city,
        'selected_address': selected_address,
        'addresses': addresses,
        'total_price': total_price,
    })

@login_required
def orders(request):
    order = Order.objects.filter(user=request.user).annotate(
        total_price=Sum(
            F('iteminorder__price') * F('iteminorder__count'),
            output_field=DecimalField()
        ),
        total_count=Sum('iteminorder__count')
    )
    return render(request, 'app/orders.html', {'order': order})

class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'app/orders.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).annotate(
            total_price=Sum(
                F('iteminorder__price') * F('iteminorder__count'),
                output_field=DecimalField()
            ),
            total_count=Sum('iteminorder__count')
        )

@login_required
def delete_order(request, pk):
    order = Order.objects.filter(user=request.user, pk=pk, status='new')
    if order:
        order.delete()
    return redirect('orders')

@login_required
def to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    item_in_cart = Cart.objects.filter(user=request.user, product=product).first()
    if item_in_cart:
        if item_in_cart.count + 1 > item_in_cart.product.count:
            return JsonResponse({'error': 'Нельзя больше добавить'})
        item_in_cart.count += 1
        item_in_cart.save()
    else:
        item_in_cart = Cart.objects.create(user=request.user, product=product, count=1 )
    return JsonResponse({'count': item_in_cart.count})

@login_required
def remove_to_cart(request, pk):
    item_in_cart = Cart.objects.filter(user=request.user, product=pk).first()
    if not item_in_cart:
        return JsonResponse({'error' : 'Не найдено'})
    if item_in_cart.count - 1 == 0:
        item_in_cart.delete()
        return JsonResponse({'deleted': True})
    item_in_cart.count -= 1
    item_in_cart.save()
    return  JsonResponse({'count': item_in_cart.count})

@login_required
def delete_from_cart(request, pk):
    item = Cart.objects.filter(user=request.user, product_id=pk).first()

    if not item:
        return JsonResponse({'error': 'Не найдено'}, status=404)

    item.delete()

    return JsonResponse({'deleted': True})

@login_required
def set_city(request):
    city_id = request.GET.get('city_id')
    request.session['city_id'] = city_id

    city = City.objects.filter(id=city_id).first()

    return JsonResponse({
        'status': 'ok',
        'city_name': city.name if city else ''
    })

@login_required
def get_addresses(request):
    city_id = request.session.get('city_id')
    addresses = Address.objects.filter(city_id=city_id)
    data = list(addresses.values('id', 'name'))
    return JsonResponse({'data': data})

@login_required
def set_address(request):
    address_id = request.GET.get('address_id')
    request.session['address_id'] = address_id

    return JsonResponse({'status': 'ok'})

@login_required
def get_cart_total(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_count = cart_items.aggregate(total=Sum('count'))['total'] or 0
    total_price = cart_items.aggregate(
        total=Sum(F('count') * F('product__price'))
    )['total'] or 0
    return JsonResponse({
        'total_count': total_count,
        'total_price': total_price
    })
