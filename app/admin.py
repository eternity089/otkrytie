from django.contrib import admin
from .models import *
from .forms import OrderForm
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = ('date','user','count_product')
    form = OrderForm
    fields = ('status', 'reject_reason')



admin.site.register(User)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
admin.site.register(City)
admin.site.register(Address)