from rest_framework import serializers

from django.contrib.auth.models import User
from users.models import SavedProgram
from hill.models import HillProgram, HillGame
import json

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
# class JSONSerializerField(serializers.Field):
#     def to_internal_value(self, data):
#         return json.dumps(data)

#     def to_representation(self, value):
#         return json.loads(value)


class HillGameSerializer(serializers.ModelSerializer):
    games = serializers.JSONField()
    left = serializers.CharField(source="left.name")
    right = serializers.CharField(source="right.name")
    class Meta:
        fields = ("left", "right", "points", "games")
        model = HillGame

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["games"] = json.loads(ret["games"])
        return ret