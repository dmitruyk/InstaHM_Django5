# quiz/views.py
import json
import random
import unicodedata
from difflib import SequenceMatcher
from math import isclose

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attempt, AttemptQuestion, Player, Question
from .serializers import AttemptSerializer, QuestionSerializer

# --- Helpers ------------------------------------------------------------


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s.strip().lower())
    return " ".join(s.split())


def fuzzy_equal(a: str, b: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, norm_text(a), norm_text(b)).ratio() >= threshold


def grade_attempt_question(aq: AttemptQuestion, q: Question) -> None:
    """Grade one AttemptQuestion in place."""
    if aq.qtype == Question.SINGLE:
        correct_ids = list(
            q.choices.filter(is_correct=True).values_list("id", flat=True)
        )
        aq.is_correct = set(aq.selected_choice_ids) == set(correct_ids)
        aq.correct_choice_ids = correct_ids

    elif aq.qtype == Question.MULTI:
        correct_ids = list(
            q.choices.filter(is_correct=True).values_list("id", flat=True)
        )
        aq.is_correct = set(aq.selected_choice_ids) == set(correct_ids)
        aq.correct_choice_ids = correct_ids

    elif aq.qtype == Question.NUM:
        if aq.numeric_response is not None and q.numeric_answer is not None:
            aq.is_correct = isclose(
                aq.numeric_response, q.numeric_answer, rel_tol=0, abs_tol=1e-6
            )

    elif aq.qtype == Question.TEXT:
        if aq.text_response and q.text_answer:
            aq.is_correct = fuzzy_equal(aq.text_response, q.text_answer)

    elif aq.qtype == Question.IMAGE:
        aq.is_correct = bool(aq.image) and (not q.image_required or aq.image.size > 0)

    aq.save()


# --- Views --------------------------------------------------------------


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().prefetch_related("choices")
    serializer_class = QuestionSerializer


class PlayStartView(APIView):
    """Start a quiz attempt for a given player_uuid."""

    def post(self, request, *args, **kwargs):
        player_uuid = request.data.get("player_uuid")
        if not player_uuid:
            return Response({"error": "player_uuid is required"}, status=400)

        player, _ = Player.objects.get_or_create(player_uuid=player_uuid)

        # Pick 5 random questions
        questions = list(Question.objects.all())
        if len(questions) < 5:
            return Response({"error": "Not enough questions in bank"}, status=400)
        selected = random.sample(questions, 5)

        attempt = Attempt.objects.create(player=player, total=len(selected))
        for q in selected:
            aq = AttemptQuestion.objects.create(
                attempt=attempt,
                question=q,
                prompt=q.prompt,
                qtype=q.qtype,
                correct_choice_ids=list(
                    q.choices.filter(is_correct=True).values_list("id", flat=True)
                ),
            )
            aq.save()

        return Response(AttemptSerializer(attempt).data, status=201)


def _coerce_to_dict(value):
    # already a mapping (e.g., parsed JSON from application/json)
    if isinstance(value, dict):
        return value
    # JSON string
    if isinstance(value, str):
        return json.loads(value or "{}")
    # Uploaded file (e.g., answers.json)
    if hasattr(value, "read"):
        raw = value.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="strict")
        return json.loads(raw or "{}")
    # Fallback
    return {}


class PlaySubmitView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _parse_answers(self, request):
        """
        Accepts:
          - multipart/form-data with 'answers' as a text field (JSON string)
          - multipart/form-data with 'answers' as a file part
          - application/json body: either {"answers": {...}} or just {...}
        Returns a dict mapping attemptQuestionId -> answer dict.
        """
        # 1) Try JSON body directly
        data = request.data
        # When JSON body: request.data is already a dict
        if isinstance(data, dict) and data:
            raw = data.get("answers", data)
            if isinstance(raw, dict):
                return raw

        # 2) Try text field in multipart/form-data
        raw_field = request.data.get("answers")
        if isinstance(raw_field, (str, bytes)):
            try:
                return json.loads(raw_field)
            except Exception:
                pass

        # 3) Try file part in multipart/form-data
        f = request.FILES.get("answers")
        if f:
            try:
                content = f.read()
                return json.loads(content.decode("utf-8"))
            except Exception:
                pass

        # Nothing usable
        return {}

    def post(self, request, attempt_id, *args, **kwargs):
        attempt = get_object_or_404(Attempt, id=attempt_id)
        answers = self._parse_answers(request) or {}
        answers = answers.get("answers", {})

        # Accept either {"123": {...}} or {"answers": {...}}
        # (already normalized in _parse_answers)
        for aq in attempt.attempt_questions.all():
            # keys might be numeric or string
            payload = answers.get(str(aq.id)) or answers.get(aq.id) or {}

            # text
            aq.text_response = payload.get("text_response")

            # numeric (string -> float)
            nr = payload.get("numeric_response", None)
            if isinstance(nr, str):
                nr = nr.strip()
                nr = float(nr) if nr else None
            if isinstance(nr, int):
                nr = float(nr) if nr else None
            aq.numeric_response = nr

            # multiple/single choices (-> list[int])
            sel = payload.get("selected_choice_ids", [])
            try:
                sel = [int(x) for x in sel]
            except Exception:
                sel = []
            aq.selected_choice_ids = sel

            # single image for the whole submission (optional)
            if "image" in request.FILES:
                aq.image = request.FILES["image"]

            aq.save()
            grade_attempt_question(aq, aq.question)

        # finalize score (and status if you added it)
        attempt.score = sum(1 for x in attempt.attempt_questions.all() if x.is_correct)
        # attempt.status = Attempt.SUBMITTED  # if using statuses
        attempt.save()

        return Response(AttemptSerializer(attempt).data, status=status.HTTP_200_OK)


class AttemptsView(generics.ListAPIView):
    serializer_class = AttemptSerializer

    def get_queryset(self):
        player_uuid = self.request.query_params.get("player_uuid")
        if not player_uuid:
            return Attempt.objects.none()
        return Attempt.objects.filter(player__player_uuid=player_uuid).order_by(
            "-created_at"
        )


class AttemptDetailView(generics.RetrieveAPIView):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
