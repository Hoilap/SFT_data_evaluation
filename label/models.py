
from django.db import models

from django.db import models
from django.contrib.auth.models import User

class SFTData(models.Model):
    data_json = models.JSONField(verbose_name='SFT_data')
    created_at = models.DateTimeField(auto_now_add=True)

class EvaluationData(models.Model):
    system_prompt = models.TextField()
    instruction = models.TextField()
    output_1 = models.TextField()
    output_2 = models.TextField()
    ground_truth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sft = models.ForeignKey(EvaluationData, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    compare_id = models.IntegerField(null=True, blank=True)
    compare_result = models.CharField(max_length=16, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


