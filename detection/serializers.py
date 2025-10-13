from rest_framework import serializers

from detection.models import FaceEvaluation


class FileUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

class FaceEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceEvaluation
        fields = "__all__"

class FilePathSerializer(serializers.Serializer):
    image_path = serializers.CharField()
