from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id','date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','get_variations','quantity','is_active')

    def get_variations(self, obj):
        # all the variations combined
        return ", ".join([str(v) for v in obj.variations.all()])
    
    get_variations.short_description = 'Variations'

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem,CartItemAdmin)