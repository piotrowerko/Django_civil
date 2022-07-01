from rest_framework import serializers

from .models import Simple_c_calc, JsonUserQuery, JsonRectReinf

class Simple_c_calcSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Simple_c_calc
        fields = ('id', "number_field1", "number_field2")


class JsonUserQuerySerializer(serializers.ModelSerializer):
    
    username = serializers.SerializerMethodField('get_username_from_owner')
    the_json = serializers.JSONField()
    
    class Meta:
        model = JsonUserQuery
        fields = ['pk', 'title', 'the_json', 'date_added', 'username', 'slug']
    
    def get_username_from_owner(self, JsonUserQuery):
        username = JsonUserQuery.owner.username
        return username

class JsonRectReinfSerializer(serializers.ModelSerializer):
    
    username = serializers.SerializerMethodField('get_username_from_owner')
    the_input_json = serializers.JSONField()
    
    class Meta:
        model = JsonRectReinf
        fields = ['title', 'the_input_json', 'date_added', 'username', 'slug']
    
    def get_username_from_owner(self, JsonUserQuery):
        username = JsonUserQuery.owner.username
        return username
    
    