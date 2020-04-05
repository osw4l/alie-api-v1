from django.contrib.auth.models import User
from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from . import constants


# Create your models here.


class Human(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    dni = models.CharField(max_length=12, unique=True)
    birth_date = models.DateField()

    cover_dni = models.ImageField(upload_to='covers_dni')
    back_cover_dni = models.ImageField(upload_to='back_cover_dni')
    photo = models.ImageField(upload_to='covers')

    class Meta:
        verbose_name = 'Human'
        verbose_name_plural = 'Humans'

    def get_full_name(self):
        return '{} {}'.format(
            self.first_name,
            self.last_name
        )

    def get_photo(self):
        return self.photo
