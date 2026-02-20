from pathlib import Path
from django import forms
from django.conf import settings

from .models import Attraction, BlogPost, GroupTour, Include, ToursDay


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class EnglishClearableFileInput(forms.ClearableFileInput):
    """File upload widget with English labels (Currently / Change / Clear)."""
    initial_text = "Currently"
    input_text = "Change"
    clear_checkbox_label = "Clear"


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        if data:
            return [single_file_clean(data, initial)]
        return []


class BaseCatalogForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.NumberInput)):
                field.widget.attrs.setdefault("class", "catalog-input")
            if isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.setdefault("class", "catalog-select-multiple")


class AttractionForm(BaseCatalogForm):
    class Meta:
        model = Attraction
        fields = ["title", "description", "city", "address", "duration_hours", "photo"]
        labels = {
            "title": "Title",
            "description": "Description",
            "city": "City",
            "address": "Address",
            "duration_hours": "Duration (hours)",
            "photo": "Photo",
        }


class IncludeForm(BaseCatalogForm):
    icon_path = forms.ChoiceField(
        required=False,
        label="Icon from media",
        choices=(),
        help_text="Choose an icon file from the server media folder.",
    )

    class Meta:
        model = Include
        fields = ["description", "icon_path"]
        labels = {
            "description": "Description",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        media_root = Path(settings.MEDIA_ROOT)
        allowed_ext = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
        icon_choices = [("", "---------")]

        if media_root.exists():
            for file_path in sorted(media_root.rglob("*")):
                if file_path.is_file() and file_path.suffix.lower() in allowed_ext:
                    rel_path = file_path.relative_to(media_root).as_posix()
                    icon_choices.append((rel_path, rel_path))

        self.fields["icon_path"].choices = icon_choices
        self.fields["icon_path"].widget.attrs.setdefault("class", "catalog-input")


class ToursDayForm(BaseCatalogForm):
    attractions = forms.ModelMultipleChoiceField(
        queryset=Attraction.objects.none(),
        required=False,
        label="Attractions",
        widget=forms.SelectMultiple,
    )
    includes = forms.ModelMultipleChoiceField(
        queryset=Include.objects.none(),
        required=False,
        label="Includes",
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = ToursDay
        fields = ["title", "description", "city", "address", "duration_hours", "photo", "attractions", "includes"]
        labels = {
            "title": "Title",
            "description": "Description",
            "city": "City",
            "address": "Address",
            "duration_hours": "Duration (hours)",
            "photo": "Photo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attractions"].queryset = Attraction.objects.order_by("title")
        self.fields["includes"].queryset = Include.objects.order_by("description")

        if self.instance and self.instance.pk:
            self.initial["attractions"] = self.instance.attractions.all()
            self.initial["includes"] = self.instance.includes.all()


class GroupTourForm(BaseCatalogForm):
    tour_days = forms.ModelMultipleChoiceField(
        queryset=ToursDay.objects.none(),
        required=False,
        label="Tour days",
        widget=forms.SelectMultiple,
    )
    media_files = MultipleFileField(
        required=False,
        label="Photos/videos",
        widget=MultipleFileInput,
    )

    class Meta:
        model = GroupTour
        fields = ["title", "short_description", "description", "group_size", "tour_days", "media_files"]
        labels = {
            "title": "Title",
            "short_description": "Short description",
            "description": "Description",
            "group_size": "Group size",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tour_days"].queryset = ToursDay.objects.order_by("title")
        if self.instance and self.instance.pk:
            self.initial["tour_days"] = self.instance.tour_days.all()


class BlogPostForm(BaseCatalogForm):
    class Meta:
        model = BlogPost
        fields = ["title", "body", "published_at", "image"]
        labels = {
            "title": "Title",
            "body": "Post body",
            "published_at": "Publication date",
            "image": "Image",
        }
        widgets = {
            "published_at": forms.DateInput(
                attrs={"type": "text", "placeholder": "YYYY-MM-DD"},
                format="%Y-%m-%d",
            ),
            "image": EnglishClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%d", "%d.%m.%Y"]
        if self.instance and self.instance.pk and self.instance.published_at:
            self.initial["published_at"] = self.instance.published_at.strftime("%Y-%m-%d")
