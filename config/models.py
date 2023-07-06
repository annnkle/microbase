from django.db import models


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255)
    
    
class AllowedValues(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    value = models.CharField(max_length=255)



