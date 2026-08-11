from django.db import models

LANGUAGE_CHOICES = [
    ("python", "Python"),
    ("html", "HTML"),
    ("css", "CSS"),
    ("js", "JavaScript"),
    ("bash", "Bash"),
    ("text", "Plain Text"),
]

class Tutorial(models.Model):
    DIFFICULTY_CHOICES = [
        ("beginner",     "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced",     "Advanced"),
    ]

    RESOURCE_TYPE_CHOICES = [
        ("workshop_tutorial", "Python & AI Tutorial"),
        ("organisers_manual", "Organiser's Manual"),
        ("mentoring_guide",   "Mentoring Guide"),
        ("extension",         "Tutorial Extension"),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField(
        blank=True,
        help_text=(
            "Legacy plain-text field — leave blank if you're using the "
            "Sections below. If filled, it renders above any sections."
        )
    )
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default="beginner"
    )
    resource_type = models.CharField(
        max_length=30,
        choices=RESOURCE_TYPE_CHOICES,
        default="workshop_tutorial",
        help_text="Classifies this tutorial on the Resources page."
    )
    estimated_minutes = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="Estimated read/build time in minutes, shown on the card and detail page."
    )
    cover_image = models.ImageField(
        upload_to="tutorials/", blank=True, null=True,
        help_text="Optional banner shown at the top of the tutorial detail page."
    )
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "content_tutorial"

    def __str__(self):
        return self.title


class TutorialSection(models.Model):
    """
    One content block inside a Tutorial.
    Each section can have a heading, prose, and/or a code example.
    Add as many sections as you need — they display in `order` order.
    """
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE, related_name="sections")
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Sections are displayed lowest → highest. 0 = first."
    )
    heading = models.CharField(
        max_length=300, blank=True,
        help_text="Optional section heading (renders as <h2> on the page)."
    )
    body = models.TextField(
        blank=True,
        help_text=(
            "Prose for this section. "
            "Leave a blank line between paragraphs — they will each render as separate <p> tags."
        )
    )
    code_block = models.TextField(
        blank=True,
        help_text=(
            "Paste your code here exactly as you want it to appear. "
            "Indentation and line breaks are preserved. Leave blank if no code for this section."
        )
    )
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default="python",
        help_text="Syntax-highlighting language for the code block above."
    )

    class Meta:
        ordering = ["order"]
        db_table = "content_tutorialsection"

    def __str__(self):
        return f"Section {self.order}: {self.heading or '(no heading)'}"
