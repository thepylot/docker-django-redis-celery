from django.db import models


# Create your models here.
class Prediction(models.Model):
    date = models.DateTimeField()
    country =models.CharField(max_length=50)
    league =models.CharField(max_length=50)
    fixture =models.CharField(max_length=50)
    home_win =models.IntegerField()
    draw =models.IntegerField()
    away_win =models.IntegerField()
    home_form =models.IntegerField()
    away_form =models.IntegerField()

    def __str__(self):
        return self.fixture

    class Meta:
        ordering = ['date','-home_win', '-away_win']