from rest_framework import serializers

from django.contrib.auth.models import User
from users.models import SavedProgram

class SavedProgramSerializer(serializers.ModelSerializer):
    # TODO: return author name instead of id
    class Meta:
        fields = ("pk", "author", "name", "private", "created", "updated", "content")
        model = SavedProgram

class SavedProgramModifySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("author", "name", "private", "content")
        model = SavedProgram