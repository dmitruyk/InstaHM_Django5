from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (AttemptDetailView, AttemptsView, PlayStartView,
                    PlaySubmitView, QuestionViewSet)

router = DefaultRouter()
router.register(r"questions", QuestionViewSet, basename="question")

urlpatterns = [
    path("play/start/", PlayStartView.as_view(), name="play-start"),
    path("play/submit/<int:attempt_id>/", PlaySubmitView.as_view(), name="play-submit"),
    path("attempts/", AttemptsView.as_view(), name="attempts"),
    path("attempts/<int:pk>/", AttemptDetailView.as_view(), name="attempt-detail"),
]
urlpatterns += router.urls
