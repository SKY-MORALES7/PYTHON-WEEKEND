from django import forms
from .models import Form, Question, Answer


class DynamicApplicationForm(forms.Form):
    """
    Dynamically builds a Django form from the Questions
    attached to an applications.Form instance.
    """

    def __init__(self, *args, application_form=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.application_form = application_form
        if application_form is None:
            return

        # Order questions so Full Name and Email always appear first
        questions = list(application_form.questions.all())

        def question_sort_key(q):
            title_lower = q.title.lower()
            if "name" in title_lower:
                return (0, q.order)
            if q.question_type == "email" or "email" in title_lower:
                return (1, q.order)
            return (2, q.order)

        questions.sort(key=question_sort_key)

        for question in questions:
            field_name = f"question_{question.pk}"
            if question.question_type == "paragraph":
                self.fields[field_name] = forms.CharField(
                    label=question.title,
                    help_text=question.help_text,
                    required=question.is_required,
                    widget=forms.Textarea(attrs={"rows": 4}),
                )
            elif question.question_type == "email":
                self.fields[field_name] = forms.EmailField(
                    label=question.title,
                    help_text=question.help_text,
                    required=question.is_required,
                )
            elif question.question_type == "url":
                self.fields[field_name] = forms.URLField(
                    label=question.title,
                    help_text=question.help_text,
                    required=question.is_required,
                )
            elif question.question_type == "number":
                self.fields[field_name] = forms.IntegerField(
                    label=question.title,
                    help_text=question.help_text,
                    required=question.is_required,
                )
            elif question.question_type == "choices":
                choices_list = [
                    (c.strip(), c.strip())
                    for c in question.choices.splitlines()
                    if c.strip()
                ]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.title,
                    help_text=question.help_text,
                    required=question.is_required,
                    choices=[("", "---------")] + choices_list,
                )
            else:  # default: text
                self.fields[field_name] = forms.CharField(
                    label=question.title,
                    help_text=question.help_text,
                    required=question.is_required,
                )

    def save_answers(self, applicant_email):
        """Persist answers for every question."""
        answers = []
        for question in self.application_form.questions.all():
            field_name = f"question_{question.pk}"
            value = self.cleaned_data.get(field_name, "")
            answer = Answer.objects.create(
                question=question,
                applicant_email=applicant_email,
                answer=str(value),
            )
            answers.append(answer)
        return answers
