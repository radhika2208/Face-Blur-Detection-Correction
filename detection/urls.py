from django.urls import path
from detection.views import ImageUploadAPI, faceDetectionAndBlurAnalysisAPI, getAllDetectionsAndCorrectionsAPI

urlpatterns = [
    path('uploadImage/', ImageUploadAPI.as_view(), name='uploadImage'),
    path('faceDetectionAndBlurAnalysis/', faceDetectionAndBlurAnalysisAPI.as_view(), name='faceDetectionAndBlurAnalysis'),
    path('getAllDetectionsAndCorrections/', getAllDetectionsAndCorrectionsAPI.as_view(), name='faceDetectionAndBlurAnalysis'),
]
