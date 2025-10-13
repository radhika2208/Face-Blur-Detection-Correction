from django.db import models


class FaceEvaluation(models.Model):
    image_path = models.CharField(max_length=500)
    is_human_face = models.BooleanField(default=False)
    is_blurry = models.BooleanField(default=False)
    corrected_image_url = models.CharField(max_length=500, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation {self.id}"
