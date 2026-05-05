from django.db.models import Sum

from .forms import RegisterUserForm, LoginForm
from .models import City, Category, Cart


def current_city(request):
    city_id = request.session.get("city_id")
    city = None
    if city_id:
        city = City.objects.filter(id=city_id).first()
    if not city:
        city = City.objects.first()
    return {
        "current_city": city,
        "cities": City.objects.all()
    }

def categories_processor(request):
    return {
        "categories": Category.objects.all()
    }

def register_form(request):
    return {
        'register_form' : RegisterUserForm()
    }

def login_form(request):
    return {
        'login_form' : LoginForm()
    }

def cart_count(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).aggregate(total=Sum('count'))['total'] or 0
    else:
        count = 0
    return {'cart_count': count}