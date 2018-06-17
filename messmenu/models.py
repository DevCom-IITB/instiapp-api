from django.db import models


class MenuDetails(models.Model):
	day = models.CharField(max_length=10,blank=True)
	breakfast = models.TextField(blank=True)
	lunch = models.TextField(blank=True)
	snacks = models.TextField(blank=True)
	dinner = models.TextField(blank=True)
	hostel = models.CharField(max_length=40,blank=True)

class Hostel(models.Model):
	hostel = models.CharField(max_length=40,blank=True)
	WeeklyMenu = models.ForeignKey(self.MenuDetails, on_delete=models.CASCADE)
# Create your models here.
