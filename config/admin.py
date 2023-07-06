from django.contrib import admin
from .models import Category, AllowedValues
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(AllowedValues)
class AllowedValuesAdmin(admin.ModelAdmin):
    pass