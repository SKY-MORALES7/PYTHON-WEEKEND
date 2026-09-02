from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────────
#  BLOG
# ─────────────────────────────────────────────

class BlogPost(models.Model):
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
    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    author = models.CharField(max_length=200, blank=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


LANGUAGE_CHOICES = [
    ("python",     "Python"),
    ("javascript", "JavaScript"),
    ("html",       "HTML"),
    ("css",        "CSS"),
    ("bash",       "Bash / Shell"),
    ("json",       "JSON"),
    ("sql",        "SQL"),
    ("plaintext",  "Plain text"),
]


class BlogSection(models.Model):
    """
    One content block inside a BlogPost.
    Order them however you like with the `order` field.
    Each section has optional heading, prose body, and an optional code block.
    """
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="sections")
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Sections are displayed lowest → highest. 0 = first."
    )
    heading = models.CharField(
        max_length=300, blank=True,
        help_text="Optional section heading (renders as <h2>)."
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
            "Indentation and line breaks are preserved."
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

    def __str__(self):
        return f"Section {self.order}: {self.heading or '(no heading)'}"


# ─────────────────────────────────────────────



# ─────────────────────────────────────────────
#  EVENT  (unchanged)
# ─────────────────────────────────────────────

# class Event(models.Model):
#     # ── Core ──────────────────────────────────────────────
#     title = models.CharField(max_length=300)
#     slug = models.SlugField(unique=True)
#     tagline = models.CharField(
#         max_length=300, blank=True,
#         help_text="Short headline in the hero, e.g. 'Build your first app this weekend!'"
#     )
#     image = models.ImageField(
#         upload_to="events/", blank=True, null=True,
#         help_text="Banner image shown on the event card and detail page hero"
#     )

#     # ── Dates & Location ──────────────────────────────────
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#     location = models.CharField(max_length=300, blank=True)
#     venue_name = models.CharField(
#         max_length=300, blank=True,
#         help_text="e.g. Code Campus Nigeria, Floor 3"
#     )
#     city = models.CharField(max_length=200, blank=True)

#     # ── About ─────────────────────────────────────────────
#     description = models.TextField(
#         blank=True,
#         help_text="General description shown above the schedule"
#     )

#     # ── Schedule ──────────────────────────────────────────
#     day1_title    = models.CharField(max_length=200, blank=True, help_text="e.g. Installation Party & Setup")
#     day1_schedule = models.TextField(blank=True, help_text="One item per line, e.g.\n09:00 — Registration\n10:00 — Welcome Session")
#     day2_title    = models.CharField(max_length=200, blank=True, help_text="e.g. Python & Django Workshop")
#     day2_schedule = models.TextField(blank=True, help_text="One item per line")
#     day3_title    = models.CharField(max_length=200, blank=True, help_text="e.g. Project Showcase — leave blank if no Day 3")
#     day3_schedule = models.TextField(blank=True, help_text="One item per line — leave blank if no Day 3")

#     # ── What you'll learn & Who should apply ─────────────
#     what_you_learn   = models.TextField(blank=True, help_text="One bullet per line, e.g.\nPython fundamentals\nDjango models and views")
#     who_should_apply = models.TextField(blank=True, help_text="One bullet per line, e.g.\nComplete beginners\nPeople switching careers")

#     # ── FAQ ───────────────────────────────────────────────
#     faq = models.TextField(
#         blank=True,
#         help_text=(
#             "Q&A pairs separated by a blank line. Format:\n"
#             "Q: Do I need experience?\n"
#             "A: No, beginners are welcome!\n\n"
#             "Q: Should I bring a laptop?\n"
#             "A: Yes please."
#         )
#     )

#     # ── Applications ─────────────────────────────────────
#     application_deadline = models.DateField(blank=True, null=True, help_text="Date applications close")
#     application_open     = models.BooleanField(default=True, help_text="Show the Register Interest button on the event page")

#     # ── Meta ─────────────────────────────────────────────
#     published  = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["start_date"]

#     def __str__(self):
#         return self.title

#     @property
#     def is_upcoming(self):
#         if not getattr(self, "start_date", None):
#             return False
#         return self.start_date >= timezone.now()

#     def day1_schedule_lines(self):
#         return [l.strip() for l in self.day1_schedule.splitlines() if l.strip()]

#     def day2_schedule_lines(self):
#         return [l.strip() for l in self.day2_schedule.splitlines() if l.strip()]

#     def day3_schedule_lines(self):
#         return [l.strip() for l in self.day3_schedule.splitlines() if l.strip()]

#     def what_you_learn_lines(self):
#         return [l.strip() for l in self.what_you_learn.splitlines() if l.strip()]

#     def who_should_apply_lines(self):
#         return [l.strip() for l in self.who_should_apply.splitlines() if l.strip()]

#     def faq_pairs(self):
#         pairs = []
#         current_q = None
#         current_a = []
#         for line in self.faq.splitlines():
#             line = line.strip()
#             if line.startswith("Q:"):
#                 if current_q:
#                     pairs.append((current_q, " ".join(current_a).strip()))
#                 current_q = line[2:].strip()
#                 current_a = []
#             elif line.startswith("A:") and current_q:
#                 current_a.append(line[2:].strip())
#             elif line and current_q:
#                 current_a.append(line)
#         if current_q:
#             pairs.append((current_q, " ".join(current_a).strip()))
#         return pairs

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from coach.models import Coach
from sponsors.models import Sponsor

class Event(models.Model):
    # ── Core ──────────────────────────────────────────────
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(
        max_length=300, blank=True,
        help_text="Short headline in the hero, e.g. 'Build your first app this weekend!'"
    )
    image = models.ImageField(
        upload_to="events/", blank=True, null=True,
        help_text="Banner image shown on the event card and detail page hero"
    )

    # ── Dates & Location ──────────────────────────────────
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=300, blank=True)
    venue_name = models.CharField(
        max_length=300, blank=True,
        help_text="e.g. Code Campus Nigeria, Floor 3"
    )
    city = models.CharField(max_length=200, blank=True)
    country = models.CharField(
        max_length=200, blank=True,
        help_text="Country where the event is held (used for map and footer counters)."
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True,
        help_text="GPS latitude — used on the event map page."
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True,
        help_text="GPS longitude — used on the event map page."
    )
    attendees_count = models.PositiveIntegerField(
        default=0,
        help_text="Verified number of people who attended this event. Update after the event."
    )

    # ── About ─────────────────────────────────────────────
    description = models.TextField(
        blank=True,
        help_text="General description shown above the schedule"
    )

    # ── Schedule ──────────────────────────────────────────
    day1_title    = models.CharField(max_length=200, blank=True, help_text="e.g. Installation Party & Setup")
    day1_schedule = models.TextField(blank=True, help_text="One item per line...")
    day2_title    = models.CharField(max_length=200, blank=True, help_text="e.g. Python & Django Workshop")
    day2_schedule = models.TextField(blank=True, help_text="One item per line")
    day3_title    = models.CharField(max_length=200, blank=True, help_text="e.g. Project Showcase...")
    day3_schedule = models.TextField(blank=True, help_text="One item per line...")

    # ── What you'll learn & Who should apply ─────────────
    what_you_learn   = models.TextField(blank=True)
    who_should_apply = models.TextField(blank=True)

    # ── FAQ ───────────────────────────────────────────────
    faq = models.TextField(blank=True)

    # ── Applications ─────────────────────────────────────
    application_deadline = models.DateField(blank=True, null=True)
    application_open     = models.BooleanField(default=True)

    # ── Meta ─────────────────────────────────────────────
    published  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ── Customization ────────────────────────────────────
    custom_html = models.TextField(blank=True, help_text="Custom HTML to include on the event page")
    custom_css = models.TextField(blank=True, help_text="Custom CSS to include on the event page")
    sponsors_title = models.CharField(max_length=255, blank=True, default='', help_text="Override the 'Sponsors' section title")
    schedule_title = models.CharField(max_length=255, blank=True, default='', help_text="Override the 'Schedule' section title")

    # ── Owner ────────────────────────────────────────────
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_events",
        help_text="The approved event organizer responsible for this specific execution."
    )

    # ── Coaches & Sponsors (M2M via through-models) ───────
    coaches = models.ManyToManyField(
        Coach,
        through="EventCoach",
        related_name="events",
        blank=True,
    )
    sponsors = models.ManyToManyField(
        Sponsor,
        through="EventSponsor",
        related_name="events",
        blank=True,
    )

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return self.title

    # ... keeping all your helper property / utility split lines functions exactly the same ...
    
    @property
    def is_upcoming(self):
        if not getattr(self, "start_date", None):
            return False
        return self.start_date >= timezone.now()

    def day1_schedule_lines(self):
        return [l.strip() for l in self.day1_schedule.splitlines() if l.strip()]

    def day2_schedule_lines(self):
        return [l.strip() for l in self.day2_schedule.splitlines() if l.strip()]

    def day3_schedule_lines(self):
        return [l.strip() for l in self.day3_schedule.splitlines() if l.strip()]

    def what_you_learn_lines(self):
        return [l.strip() for l in self.what_you_learn.splitlines() if l.strip()]

    def who_should_apply_lines(self):
        return [l.strip() for l in self.who_should_apply.splitlines() if l.strip()]

    def faq_pairs(self):
        pairs = []
        current_q = None
        current_a = []
        for line in self.faq.splitlines():
            line = line.strip()
            if line.startswith("Q:"):
                if current_q:
                    pairs.append((current_q, " ".join(current_a).strip()))
                current_q = line[2:].strip()
                current_a = []
            elif line.startswith("A:") and current_q:
                current_a.append(line[2:].strip())
            elif line and current_q:
                current_a.append(line)
        if current_q:
            pairs.append((current_q, " ".join(current_a).strip()))
        return pairs


# ─────────────────────────────────────────────
#  WEBSITE CONTENT
# ─────────────────────────────────────────────

class WebsiteContent(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    location_identifier = models.CharField(max_length=100, unique=True, help_text="e.g. 'home_about_section', 'footer_text'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Website Content"

    def __str__(self):
        return self.title

# ─────────────────────────────────────────────
#  WEBSITE MENUS
# ─────────────────────────────────────────────

class WebsiteMenus(models.Model):
    POSITION_CHOICES = [
        ("header", "Header"),
        ("footer", "Footer"),
        ("sidebar", "Sidebar"),
    ]
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255, help_text="Can be a named URL pattern or absolute URL")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default="header")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position", "order"]
        verbose_name_plural = "Website Menus"

    def __str__(self):
        return f"{self.name} ({self.get_position_display()})"


# ─────────────────────────────────────────────
#  EVENT ↔ COACH  (through-model)
# ─────────────────────────────────────────────

class EventCoach(models.Model):
    """Links a Coach to an Event, with an optional per-event role and display order."""
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_coaches"
    )
    coach = models.ForeignKey(
        Coach, on_delete=models.CASCADE, related_name="event_assignments"
    )
    role = models.CharField(
        max_length=200, blank=True,
        help_text="Override the coach's default role for this event, e.g. 'Lead Mentor'."
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Lower numbers appear first in the coach list."
    )

    class Meta:
        ordering = ["order"]
        unique_together = [("event", "coach")]
        verbose_name = "Event Coach"
        verbose_name_plural = "Event Coaches"

    def __str__(self):
        return f"{self.coach.name} @ {self.event.title}"


# ─────────────────────────────────────────────
#  EVENT ↔ SPONSOR  (through-model)
# ─────────────────────────────────────────────

class EventSponsor(models.Model):
    """Links a Sponsor to an Event, with an optional description override and display order."""
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_sponsors"
    )
    sponsor = models.ForeignKey(
        Sponsor, on_delete=models.CASCADE, related_name="event_appearances"
    )
    description = models.CharField(
        max_length=300, blank=True,
        help_text="Short blurb about this sponsor's contribution to this specific event."
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Lower numbers appear first in the sponsor list."
    )

    class Meta:
        ordering = ["order"]
        unique_together = [("event", "sponsor")]
        verbose_name = "Event Sponsor"
        verbose_name_plural = "Event Sponsors"

    def __str__(self):
        return f"{self.sponsor.name} @ {self.event.title}"
