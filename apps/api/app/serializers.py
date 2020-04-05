from rest_framework import serializers
from apps.app import models


class HumanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Human
        fields = (
            'id',
            'first_name',
            'last_name',
            'dni',
            'birth_date',
            'cover_dni',
            'back_cover_dni',
            'photo'
        )


