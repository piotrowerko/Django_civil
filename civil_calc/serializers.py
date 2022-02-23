from rest_framework import serializers

from .models import Simple_c_calc

class Simple_c_calcSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Simple_c_calc
        fields = ('id', "number_field1", "number_field2")