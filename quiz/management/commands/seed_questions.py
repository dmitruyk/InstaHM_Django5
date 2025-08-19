from django.core.management.base import BaseCommand

from quiz.models import Category, Choice, Question


class Command(BaseCommand):
    help = "Seed sample questions (10)"

    def handle(self, *args, **kwargs):
        cat, _ = Category.objects.get_or_create(name="General")

        # 1 Text
        q = Question.objects.create(
            prompt="What is the capital of France?",
            qtype=Question.TEXT,
            category=cat,
            difficulty=Question.EASY,
            text_answer="Paris",
        )

        # 2 Numeric
        q = Question.objects.create(
            prompt="2 + 2 = ?",
            qtype=Question.NUM,
            category=cat,
            difficulty=Question.EASY,
            numeric_answer=4,
        )

        # 3 Image
        q = Question.objects.create(
            prompt="Upload a picture of anything (demo).",
            qtype=Question.IMAGE,
            category=cat,
            difficulty=Question.EASY,
            image_required=True,
        )

        # 4 Single choice
        q = Question.objects.create(
            prompt="Select the primary color.",
            qtype=Question.SINGLE,
            category=cat,
            difficulty=Question.EASY,
        )
        Choice.objects.bulk_create(
            [
                Choice(question=q, text="Green", is_correct=False),
                Choice(question=q, text="Blue", is_correct=True),
                Choice(question=q, text="Orange", is_correct=False),
            ]
        )

        # 5 Multiple choice
        q = Question.objects.create(
            prompt="Select all even numbers.",
            qtype=Question.MULTI,
            category=cat,
            difficulty=Question.EASY,
        )
        Choice.objects.bulk_create(
            [
                Choice(question=q, text="1", is_correct=False),
                Choice(question=q, text="2", is_correct=True),
                Choice(question=q, text="3", is_correct=False),
                Choice(question=q, text="4", is_correct=True),
            ]
        )

        # Add 5 more quick ones
        Question.objects.create(
            prompt="Reverse of 'stressed'?",
            qtype=Question.TEXT,
            category=cat,
            difficulty=Question.MED,
            text_answer="desserts",
        )
        Question.objects.create(
            prompt="10 / 2 = ?",
            qtype=Question.NUM,
            category=cat,
            difficulty=Question.EASY,
            numeric_answer=5,
        )
        q = Question.objects.create(
            prompt="Pick the mammal.",
            qtype=Question.SINGLE,
            category=cat,
            difficulty=Question.MED,
        )
        Choice.objects.bulk_create(
            [
                Choice(question=q, text="Shark", is_correct=False),
                Choice(question=q, text="Dolphin", is_correct=True),
                Choice(question=q, text="Octopus", is_correct=False),
            ]
        )
        q = Question.objects.create(
            prompt="Select all prime numbers.",
            qtype=Question.MULTI,
            category=cat,
            difficulty=Question.MED,
        )
        Choice.objects.bulk_create(
            [
                Choice(question=q, text="2", is_correct=True),
                Choice(question=q, text="4", is_correct=False),
                Choice(question=q, text="5", is_correct=True),
                Choice(question=q, text="6", is_correct=False),
            ]
        )
        Question.objects.create(
            prompt="Name of our planet?",
            qtype=Question.TEXT,
            category=cat,
            difficulty=Question.EASY,
            text_answer="Earth",
        )

        self.stdout.write(self.style.SUCCESS("Seeded 10 questions."))
