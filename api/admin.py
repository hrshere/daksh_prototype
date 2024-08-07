from django.contrib import admin
from .models import Category, Shape, Material, Product, Rating, ProductImage

# Register your models here.

#master category model
admin.site.register(Category)
admin.site.register(Shape)
admin.site.register(Material)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of extra inline forms to display

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Rating)
