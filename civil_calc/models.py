import jsonfield

from django.db import models

from django.utils.text import slugify
from django.conf import settings
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

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
    

# def upload_location(instance, filename, **kwargs):
# 	file_path = 'blog/{author_id}/{title}-{filename}'.format(
# 			author_id=str(instance.author.id), title=str(instance.title), filename=filename
# 		) 
# 	return file_path

class JsonUserQuery(models.Model):
    """zmapowana tabela sql dotycząca jsonów podanych przez userów LUB ADMINA"""
    title = models.CharField(max_length=100, null=False, blank=True)
    #the_json = jsonfield.JSONField()
    the_json = models.JSONField()
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True, unique=True)
    def __str__(self):
        return f'this is a json query made by: {self.owner} on date: {self.date_added}'
    
def pre_save_json_receiever(sender, instance, *args, **kwargs):
    """cerates a url slug, before json query is saved"""
    if not instance.slug:
        instance.slug = slugify(instance.owner.username + "-" + instance.title)

pre_save.connect(pre_save_json_receiever, sender=JsonUserQuery)