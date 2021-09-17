from django.db import models

class AbstractBaseModel(models.Model):
    """
    This abstract model contains fields that should be contained in each model. Soft delete is also implemented in this model.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        abstract = True
