from django.db import models

# Create your models here.
class sales(models.Model):
	dailySales = models.FloatField(default = 0)
	monthlySales = models.FloatField(default = 0)
	YearlySales = models.FloatField(default = 0)
