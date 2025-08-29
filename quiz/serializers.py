# quiz/serializers.py
from typing import List, Optional

from django.db import transaction
from rest_framework import serializers

from .models import (Attempt, AttemptQuestion, Category, Choice, Player,
                     Question)

# ---------- Category ----------


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# ---------- Choice (nested under Question) ----------


class ChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]


# ---------- Question (with nested choices) ----------


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Question
        fields = [
            "id",
            "prompt",
            "qtype",
            "category",
            "difficulty",
            "text_answer",
            "numeric_answer",
            "image_required",
            "choices",
        ]

    # ---- Validation rules aligned with spec ----
    def validate(self, attrs):
        # Determine effective values (handle partial update)
        qtype = attrs.get("qtype", getattr(self.instance, "qtype", None))
        choices = attrs.get("choices", None)
        text_answer = attrs.get(
            "text_answer", getattr(self.instance, "text_answer", None)
        )
        numeric_answer = attrs.get(
            "numeric_answer", getattr(self.instance, "numeric_answer", None)
        )

        # Rules for choice-based types
        if qtype in (Question.SINGLE, Question.MULTI):
            # Require choices either in payload or existing instance
            existing_choices = []
            if self.instance and choices is None:
                existing_choices = list(
                    self.instance.choices.all().values("id", "text", "is_correct")
                )
            provided = choices if choices is not None else existing_choices
            if not provided:
                raise serializers.ValidationError(
                    "Choice questions must include at least one choice."
                )

            correct_count = sum(1 for c in provided if c.get("is_correct"))
            if qtype == Question.SINGLE and correct_count != 1:
                raise serializers.ValidationError(
                    "Single-choice question must have exactly one correct choice."
                )
            if qtype == Question.MULTI and correct_count < 1:
                raise serializers.ValidationError(
                    "Multiple-choice question must have at least one correct choice."
                )

        # Rules for text/numeric types
        if qtype == Question.TEXT and not text_answer:
            raise serializers.ValidationError("Text question requires 'text_answer'.")
        if qtype == Question.NUM and numeric_answer is None:
            raise serializers.ValidationError(
                "Numeric question requires 'numeric_answer'."
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        choices_data: Optional[List[dict]] = validated_data.pop("choices", None)
        question = Question.objects.create(**validated_data)
        if choices_data:
            for ch in choices_data:
                Choice.objects.create(question=question, **ch)
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        choices_data: Optional[List[dict]] = validated_data.pop("choices", None)

        # Update scalar fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        # Synchronize choices if provided:
        # simplest/robust approach: replace all
        if choices_data is not None:
            instance.choices.all().delete()
            for ch in choices_data:
                ch.pop("id", None)  # avoid PK reuse confusion
                Choice.objects.create(question=instance, **ch)

        return instance


# ---------- Player ----------


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ["player_uuid"]


# ---------- AttemptQuestion (review-friendly) ----------


class AttemptQuestionSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source="question.id", read_only=True)
    choices = ChoiceSerializer(
        source="question.choices", many=True, read_only=True
    )  # <— add this

    class Meta:
        model = AttemptQuestion
        fields = [
            "id",
            "question_id",
            "prompt",
            "qtype",
            "selected_choice_ids",
            "text_response",
            "numeric_response",
            "image",
            "is_correct",
            "correct_choice_ids",
            "choices",  # <— include choices
        ]
        read_only_fields = [
            "question_id",
            "prompt",
            "qtype",
            "is_correct",
            "correct_choice_ids",
            "choices",
        ]


# ---------- Attempt (with nested attempt_questions) ----------


class AttemptSerializer(serializers.ModelSerializer):
    attempt_questions = AttemptQuestionSerializer(many=True, read_only=True)
    player_uuid = serializers.UUIDField(source="player.player_uuid", read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "player_uuid",
            "created_at",
            "score",
            "total",
            "attempt_questions",
        ]
        read_only_fields = [
            "id",
            "player_uuid",
            "created_at",
            "score",
            "total",
            "attempt_questions",
        ]

