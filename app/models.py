from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    username = models.CharField(max_length=120, blank=True, null=True)
    name = models.CharField(max_length=120, verbose_name='Имя', blank=False, null=False)
    phone = models.TextField(max_length=120, verbose_name='Номер телефона', unique=True, blank=False, null=False)
    email = models.EmailField(verbose_name='Электронная почта', unique=True, blank=False)
    role = models.CharField(max_length=120, verbose_name='Роль',
                            choices=(('admin', 'Администратор'), ('user','Пользователь')), default='user')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=120, verbose_name='Название', blank=False)
    date = models.DateTimeField(verbose_name='Дата добавления', auto_now_add=True)
    photo_file = models.ImageField(max_length=120, upload_to='/products', blank=True, null=True,
                                   validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])])
    country = models.CharField(max_length=120, verbose_name='Страна производства', blank=False, null=False)
    height = models.IntegerField(verbose_name='Высота', blank=True, default=0)
    width = models.IntegerField(verbose_name='Ширина', blank=True, default=0)
    thickness = models.IntegerField(verbose_name = 'Толщина', blank=True, default=0)
    price = models.DecimalField(verbose_name='Стоимость', max_digits=10, decimal_places=2, default=0)
    count = models.IntegerField(verbose_name='Количество', blank=False, default=1)
    category = models.ForeignKey('Category', verbose_name='Категория', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Описание', blank=False, null=False)
    old_price = models.DecimalField(verbose_name='Стоимость (при наличии скидки)', max_digits=10, decimal_places=2, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('product', args=[str(self.id)])
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=120, verbose_name='Название', blank=False)
    slug = models.SlugField(max_length=120, unique=False, blank=True, null=True, verbose_name='URL')
    def __str__(self):
        return self.name

class Cart(models.Model):
    product = models.ForeignKey('Product', verbose_name='Продукт' , on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='Количество товаров', blank=False, default=0)
    user = models.ForeignKey('User', verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name + ' ' + str(self.count)

class Order(models.Model):
    STATUS_CHOICES = [
    ('new', _('Новый')),
    ('confirmed', _('Подтвержден')),
    ('delivered', _('Доставлен')),
    ('canceled', _('Отменен'))
    ]
    date = models.DateTimeField(verbose_name='Дата заказа', auto_now_add=True)
    status = models.CharField(max_length=120, verbose_name='Дата заказа' ,choices=STATUS_CHOICES, default='new', blank=False, null=False)
    reject_reason = models.TextField(verbose_name='Причина отказа', blank=True)
    user = models.ForeignKey('User', verbose_name='Пользователь', on_delete=models.CASCADE)
    products = models.ManyToManyField('Product', through='ItemInOrder', related_name='orders')
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    address = models.ForeignKey('Address', on_delete=models.CASCADE)

    def status_verbose(self):
        return dict(self.STATUS_CHOICES)[self.status]
    def count_product(self):
        count = 0
        for item_order in self.iteminorder_set.all():
            count += item_order.count
        return count
    def __str__(self):
        return self.date.ctime() + ' ' + self.user.name + ' ' + str(self.count_product())

class ItemInOrder(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='Количество', blank=False, default=0)
    price = models.DecimalField(verbose_name='Стоимость', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.order.user} - {self.product.name} - {self.count} - {self.product.price*self.count}"

class City(models.Model):
    name = models.CharField(max_length = 120)
    def __str__(self):
        return self.name

class Address(models.Model):
    city  = models.ForeignKey('City', on_delete=models.CASCADE)
    name = models.CharField(max_length = 255)
    def __str__(self):
        return self.name