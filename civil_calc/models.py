from django.db import models

class Simple_c_calc(models.Model):
    """liczby poznawane przez użytkownika"""
    number_field1 = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        )
    number_field2 = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        )
    
    def __str__(self):
        return f'{self.number_field1} {self.number_field2}'