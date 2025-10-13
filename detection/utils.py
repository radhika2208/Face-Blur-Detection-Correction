from detection.constants import face_cascade
import cv2
import numpy as np
import os

from detection.models import FaceEvaluation
from face_blur_api import settings


def is_human_face(image_path):
    """
    Returns True if a human face is detected in the image, else False.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) > 0:
        return True
    return False


def detect_blur(image_path, face_cascade, threshold=100):
    """
    Detects if the image or any detected face is blurry.
    Returns True if the image/face is blurry, else False.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image at {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    def variance_of_laplacian(image):
        """Compute Laplacian variance — higher means sharper."""
        return cv2.Laplacian(image, cv2.CV_64F).var()

    # If no face found, check overall image sharpness
    if len(faces) == 0:
        fm = variance_of_laplacian(gray)
        return fm < threshold

    blur_flags = []
    for (x, y, w, h) in faces:
        face = gray[y:y + h, x:x + w]
        face_resized = cv2.resize(face, (100, 100))
        fm = variance_of_laplacian(face_resized)
        brightness = np.mean(face_resized)
        dynamic_threshold = threshold * (0.8 if brightness > 150 else 1.2)
        is_blur = fm < dynamic_threshold
        blur_flags.append(is_blur)

    # If majority of faces are blurry, mark as blurry
    blurry_faces = sum(blur_flags)
    return blurry_faces > len(blur_flags) / 2


def correct_blur(image_path):
    """
    Sharpen and deblur a face image while preserving natural color,
    contrast, and brightness.
    """

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image not found: {image_path}")
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Step 1: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Step 2: Unsharp masking for detail recovery
    blur = cv2.GaussianBlur(enhanced_img, (0, 0), sigmaX=2)
    sharpened = cv2.addWeighted(enhanced_img, 1.8, blur, -0.8, 0)

    # Step 3: Optional bilateral filter to reduce noise while keeping edges
    sharpened = cv2.bilateralFilter(sharpened, 5, 50, 50)

    # Step 4: Clip and convert back
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    # Step 5: Save result
    processed_dir = os.path.join("media", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    corrected_name = f"{name}_unblurred{ext}"
    corrected_path = os.path.join(processed_dir, corrected_name)

    cv2.imwrite(corrected_path, sharpened)
    return corrected_path

def ensure_directory_exists(directory_path: str):
    """Create directory if not exists."""
    os.makedirs(directory_path, exist_ok=True)


def get_absolute_image_path(relative_path: str) -> str:
    """Convert /media/... relative path to absolute system path."""
    if relative_path.startswith("/media/"):
        return os.path.join(settings.BASE_DIR, relative_path.lstrip("/"))
    elif relative_path.startswith("media/"):
        return os.path.join(settings.BASE_DIR, relative_path)
    return relative_path


def create_evaluation(image_path, is_human_face, is_blurry, corrected_image_url=None):
    """Create and return a FaceEvaluation entry."""
    evaluation = FaceEvaluation.objects.create(
        image_path=image_path,
        is_human_face=is_human_face,
        is_blurry=is_blurry,
        corrected_image_url=corrected_image_url
    )
    return evaluation


def api_success(data, status_code=200):
    """Standardize success response."""
    from rest_framework.response import Response
    from rest_framework import status as drf_status
    return Response(data, status=status_code or drf_status.HTTP_200_OK)


def api_error(message, status_code=400):
    """Standardize error response."""
    from rest_framework.response import Response
    from rest_framework import status as drf_status
    return Response({"error": message}, status=status_code or drf_status.HTTP_400_BAD_REQUEST)
