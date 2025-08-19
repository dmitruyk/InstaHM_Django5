# quiz/admin.py

import csv
import io
import json

from django import forms
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (Attempt, AttemptQuestion, Category, Choice, Player,
                     Question)

# ---------- Common admin action ----------


def export_as_csv(modeladmin, request: HttpRequest, queryset):
    meta = modeladmin.model._meta
    field_names = [f.name for f in meta.fields]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, f, "") for f in field_names])
    resp = HttpResponse(buf.getvalue(), content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="{meta.model_name}.csv"'
    return resp


export_as_csv.short_description = _("Export selected as CSV")


class SmartAdmin(admin.ModelAdmin):
    list_per_page = 50
    save_on_top = True
    actions = [export_as_csv]
    list_display_links = ("id",)


# ---------- Inlines ----------


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    fields = ("id", "text", "is_correct")
    readonly_fields = ("id",)
    show_change_link = True


class AttemptQuestionInline(admin.TabularInline):
    model = AttemptQuestion
    extra = 0
    raw_id_fields = ("question",)

    def image_thumb(self, obj: AttemptQuestion):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:80px;max-width:120px;" />',
                obj.image.url,
            )
        return "-"

    image_thumb.short_description = "Image"

    def selected_preview(self, obj: AttemptQuestion):
        try:
            return (json.dumps(obj.selected_choice_ids) or "")[:140]
        except Exception:
            return (str(obj.selected_choice_ids) or "")[:140]

    selected_preview.short_description = "Selected IDs"

    def correct_preview(self, obj: AttemptQuestion):
        try:
            return (json.dumps(obj.correct_choice_ids) or "")[:140]
        except Exception:
            return (str(obj.correct_choice_ids) or "")[:140]

    correct_preview.short_description = "Correct IDs"

    fields = (
        "id",
        "question",
        "qtype",
        "text_response",
        "numeric_response",
        "is_correct",
        "selected_preview",
        "correct_preview",
        "image",
        "image_thumb",
    )
    readonly_fields = ("id", "selected_preview", "correct_preview", "image_thumb")


# ---------- Forms ----------


class AttemptQuestionForm(forms.ModelForm):
    class Meta:
        model = AttemptQuestion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make JSON fields easier to edit
        if "selected_choice_ids" in self.fields:
            self.fields["selected_choice_ids"].widget = forms.Textarea(
                attrs={"rows": 4}
            )
        if "correct_choice_ids" in self.fields:
            self.fields["correct_choice_ids"].widget = forms.Textarea(attrs={"rows": 4})


# ---------- Admin registrations ----------


@admin.register(Category)
class CategoryAdmin(SmartAdmin):
    list_display = ("id", "name", "question_count")
    search_fields = ("name",)

    def question_count(self, obj: Category) -> int:
        # default reverse name since Question.category has no related_name
        return obj.question_set.count()

    question_count.short_description = "Questions"


@admin.register(Question)
class QuestionAdmin(SmartAdmin):
    inlines = [ChoiceInline]
    raw_id_fields = ("category",)

    def prompt_short(self, obj: Question) -> str:
        s = obj.prompt or ""
        return (s[:80] + "…") if len(s) > 80 else s

    prompt_short.short_description = "Prompt"

    list_display = (
        "id",
        "prompt_short",
        "qtype",
        "difficulty",
        "category",
        "image_required",
    )
    list_filter = ("qtype", "difficulty", "category", "image_required")
    search_fields = ("id", "prompt", "choices__text")


@admin.register(Choice)
class ChoiceAdmin(SmartAdmin):
    raw_id_fields = ("question",)
    list_display_links = ("id", "question")  # allow jumping into question
    list_display = ("id", "question", "text", "is_correct")
    list_filter = (
        "is_correct",
        "question__qtype",
        "question__difficulty",
        "question__category",
    )
    search_fields = ("id", "text", "question__prompt")
    list_editable = ("is_correct",)


@admin.register(Player)
class PlayerAdmin(SmartAdmin):
    list_display = ("id", "player_uuid", "attempts_count")
    search_fields = ("player_uuid",)

    def attempts_count(self, obj: Player) -> int:
        return obj.attempts.count()

    attempts_count.short_description = "Attempts"


@admin.register(Attempt)
class AttemptAdmin(SmartAdmin):
    inlines = [AttemptQuestionInline]
    raw_id_fields = ("player",)
    list_display = ("id", "player", "created_at", "score", "total", "correct_ratio")
    list_filter = ("created_at",)
    search_fields = ("id", "player__player_uuid")

    def correct_ratio(self, obj: Attempt) -> str:
        total = obj.total or 0
        correct = obj.attempt_questions.filter(is_correct=True).count()
        pct = f"{(correct / total * 100):.0f}%" if total else "—"
        return f"{correct}/{total} ({pct})"

    correct_ratio.short_description = "Correct"


@admin.register(AttemptQuestion)
class AttemptQuestionAdmin(SmartAdmin):
    form = AttemptQuestionForm
    raw_id_fields = ("attempt", "question")
    list_display_links = ("id", "attempt")
    list_display = (
        "id",
        "attempt",
        "question",
        "qtype",
        "is_correct",
        "text_resp_short",
        "numeric_response",
        "selected_preview",
        "correct_preview",
        "image_thumb",
    )
    list_editable = ("is_correct",)
    list_filter = ("qtype", "is_correct")
    search_fields = ("id", "attempt__id", "question__prompt", "text_response")

    def text_resp_short(self, obj: AttemptQuestion) -> str:
        s = obj.text_response or ""
        return (s[:60] + "…") if len(s) > 60 else s

    text_resp_short.short_description = "Text resp"

    def selected_preview(self, obj: AttemptQuestion):
        try:
            return (json.dumps(obj.selected_choice_ids) or "")[:120]
        except Exception:
            return (str(obj.selected_choice_ids) or "")[:120]

    selected_preview.short_description = "Selected IDs"

    def correct_preview(self, obj: AttemptQuestion):
        try:
            return (json.dumps(obj.correct_choice_ids) or "")[:120]
        except Exception:
            return (str(obj.correct_choice_ids) or "")[:120]

    correct_preview.short_description = "Correct IDs"

    def image_thumb(self, obj: AttemptQuestion):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:70px;max-width:110px;" />',
                obj.image.url,
            )
        return "-"

    image_thumb.short_description = "Image"
