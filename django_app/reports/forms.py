import re

from django import forms

from .models import PotholeReport, Resident


# photo upload
class MultiplePhotoInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiplePhotoField(forms.FileField):
    widget = MultiplePhotoInput()

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        return data


# resident info
class ResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = ["name", "email", "phone_number"]

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "John Smith"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "example@email.com"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "(306) 555-1234"}
            ),
        }

        error_messages = {
            "email": {
                "required": "An email address is required so we can send you your pothole report confirmation and ticket number.",
                "invalid": "Please enter a valid email address (for example, name@example.com).",
            },
            "phone_number": {
                "required": "A phone number is required in case we need to contact you about your report.",
                "invalid": "Please enter a valid phone number (for example, (306) 555-1234).",
            },
        }

    def __init__(self, *args, **kwargs):  # for error messaging
        super().__init__(*args, **kwargs)

        self.fields["name"].required = False
        self.fields["email"].required = True
        self.fields["phone_number"].required = True

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " error"

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")

        # Remove formatting before validation
        digits = re.sub(r"\D", "", phone_number)

        if len(digits) != 10:
            # Validate phone number format (simple regex for demonstration)
            # if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise forms.ValidationError(
                "Please enter a valid phone number (for example, (306) 555-1234)."
            )
        return phone_number


# pothole info
class PotholeReportForm(forms.ModelForm):
    photos = MultiplePhotoField(required=False)

    class Meta:
        model = PotholeReport
        fields = ["address", "description"]

        widgets = {
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1234 Albert Street, Regina, SK",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Example:\n"
                    "• Approximately 40 cm wide\n"
                    "• Near Albert St. & 13th Ave.\n"
                    "• Difficult to avoid while driving",
                }
            ),
        }
        error_messages = {
            "address": {
                "required": "Please enter the address or nearest location of the pothole."
            }
        }

    def __init__(self, *args, **kwargs):  # for error messaging
        super().__init__(*args, **kwargs)

        self.fields["address"].required = True
        self.fields["description"].required = False

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        for field in self.errors:
            self.fields[field].widget.attrs["class"] += " error"

    def clean_photos(self):
        photos = self.files.getlist("photos")
        if len(photos) > 5:
            raise forms.ValidationError("You can upload a maximum of 5 photos.")
        for photo in photos:
            if photo.content_type not in ["image/jpeg", "image/png"]:
                raise forms.ValidationError(
                    "Only JPEG (.jpg, .jpeg) and PNG (.png) image files are supported."
                )
        return photos

    def clean_address(self):
        address = self.cleaned_data.get("address")

        if not address or len(address) < 5:
            raise forms.ValidationError(
                "Please enter a more complete address so we can accurately locate the pothole."
            )
        return address
