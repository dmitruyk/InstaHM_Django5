import uuid

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    TEXT = "text"
    SINGLE = "single"
    MULTI = "multi"
    NUM = "numeric"
    IMAGE = "image"
    TYPE_CHOICES = [
        (TEXT, "Text"),
        (SINGLE, "Single"),
        (MULTI, "Multiple"),
        (NUM, "Numeric"),
        (IMAGE, "Image"),
    ]
    EASY = "easy"
    MED = "med"
    HARD = "hard"
    DIFF_CHOICES = [(EASY, "Easy"), (MED, "Medium"), (HARD, "Hard")]

    prompt = models.TextField()
    qtype = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    difficulty = models.CharField(max_length=10, choices=DIFF_CHOICES)
    text_answer = models.TextField(null=True, blank=True)
    numeric_answer = models.FloatField(null=True, blank=True)
    image_required = models.BooleanField(default=False)


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class Player(models.Model):
    player_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)


class Attempt(models.Model):
    player = models.ForeignKey(
        Player, related_name="attempts", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    total = models.IntegerField(default=5)


class AttemptQuestion(models.Model):
    attempt = models.ForeignKey(
        Attempt, related_name="attempt_questions", on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    prompt = models.TextField()
    qtype = models.CharField(max_length=10)
    text_response = models.TextField(null=True, blank=True)
    numeric_response = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to="answers/", null=True, blank=True)
    selected_choice_ids = models.JSONField(default=list)
    is_correct = models.BooleanField(default=False)
    correct_choice_ids = models.JSONField(default=list)
