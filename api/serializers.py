from rest_framework import serializers

from django.contrib.auth.models import User
from users.models import SavedProgram
from hill.models import HillProgram, HillGame

class SavedProgramSerializer(serializers.ModelSerializer):
    # TODO: return author name instead of id
    class Meta:
        fields = ("pk", "author", "name", "private", "created", "updated", "content")
        model = SavedProgram

class SavedProgramModifySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("author", "name", "private", "content")
        model = SavedProgram

class HillProgramSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("author", "name", "content", "rank", "prev_rank", "points", "score")
        model = HillProgram

# https://stackoverflow.com/questions/47218977/django-deserializing-jsonfield-in-drf
class JSONSerializerField(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value

class HillGameSerializer(serializers.ModelSerializer):
    games = JSONSerializerField()
    class Meta:
        fields = ("left", "right", "points", "games")