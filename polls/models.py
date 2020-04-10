import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=300)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)
    answer_order = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.answer_text

# class isRelatedTo(models.Model):
#     question1 = models.ForeignKey(Question, related_name="question1", primary_key=True, on_delete=models.CASCADE)
#     question2 = models.ForeignKey(Question, related_name="question2", on_delete=models.CASCADE)
#     question3 = models.ForeignKey(Question, related_name="question3", on_delete=models.CASCADE)

#     def __str__(self):
#         return "<IsRelatedTo: {} {}>".format(self.question2, self.question3)

#     def getRelatedQuestion2(self):
#         return self.question2

#     def getRelatedQuestion3(self):
#         return self.question3



