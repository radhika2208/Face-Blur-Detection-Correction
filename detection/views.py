from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
import os

from detection.models import FaceEvaluation
from detection.serializers import FileUploadSerializer, FilePathSerializer, FaceEvaluationSerializer
from detection.constants import face_cascade
from detection.utils import (
    detect_blur,
    is_human_face,
    correct_blur,
    ensure_directory_exists,
    get_absolute_image_path,
    create_evaluation,
    api_success,
    api_error
)


def dashboard_view(request):
    return render(request, "dashboard.html")


class ImageUploadAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Upload image and get its relative path",
        request_body=FileUploadSerializer,
        responses={200: 'Returns {"img_path": "media/uploads/example.jpeg"}'}
    )
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data['image']

        uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        ensure_directory_exists(uploads_dir)

        temp_path = os.path.join(uploads_dir, image.name)
        with open(temp_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        return api_success({
            "img_path": os.path.join(settings.MEDIA_URL, 'uploads', image.name)
        })


class faceDetectionAndBlurAnalysisAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Detect faces and analyze blur",
        request_body=FilePathSerializer,
        responses={200: 'Returns analysis details including corrected image if blurry.'}
    )
    def post(self, request):
        serializer = FilePathSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        relative_image_path = serializer.validated_data['image_path']
        image_path = get_absolute_image_path(relative_image_path)

        if not os.path.exists(image_path):
            return api_error(f"Image not found: {image_path}")

        # Detect human face
        if not is_human_face(image_path):
            evaluation = create_evaluation(relative_image_path, False, False)
            return api_success({
                "id": evaluation.id,
                "is_human_face": False,
                "message": "Not a human face"
            })

        # Detect blur
        is_blur = detect_blur(image_path, face_cascade)
        if not is_blur:
            evaluation = create_evaluation(relative_image_path, True, False)
            return api_success({
                "id": evaluation.id,
                "is_human_face": True,
                "is_blurry": False,
                "message": "Human face detected and not blurry"
            })

        # Correct blur
        corrected_path = correct_blur(image_path)
        corrected_url = corrected_path.replace(str(settings.BASE_DIR) + '/', '')
        evaluation = create_evaluation(relative_image_path, True, True, corrected_url)
        return api_success({
            "id": evaluation.id,
            "is_human_face": True,
            "is_blurry": True,
            "corrected_image_url": corrected_url,
            "message": "Blur detected and corrected"
        })


class getAllDetectionsAndCorrectionsAPI(APIView):

    @swagger_auto_schema(
        operation_description="Get all face detection and blur correction evaluations",
        responses={200: 'List of all FaceEvaluation entries'}
    )
    def get(self, request):
        evaluations = FaceEvaluation.objects.all()
        if not evaluations.exists():
            return api_error("No evaluations found", status.HTTP_404_NOT_FOUND)

        serializer = FaceEvaluationSerializer(evaluations, many=True)
        return api_success(serializer.data)
