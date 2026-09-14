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
    what_you_learn   = models.TextField(blank=True, help_text="List the skills participants will gain. Enter one item per line.")
    who_should_apply = models.TextField(blank=True, help_text="Describe the ideal candidate. Enter one item per line.")

    # ── FAQ ───────────────────────────────────────────────
    faq = models.TextField(blank=True, help_text="Q&A pairs separated by a blank line. Format:\nQ: Do I need experience?\nA: No, beginners are welcome!")

    # ── Applications ─────────────────────────────────────
    application_deadline = models.DateField(blank=True, null=True, help_text="The date when applications will close.")
    application_open     = models.BooleanField(default=True, help_text="If checked, the 'Register Interest' button will be visible on the event page.")

    # ── Meta ─────────────────────────────────────────────
    published  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ── Customization ────────────────────────────────────
    custom_html = models.TextField(blank=True, help_text="Custom HTML block (Tailwind CSS classes supported) to include on the event page. You do not need a separate CSS field.")
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
#  PAGE CONTENT  (editable text fields per page)
# ─────────────────────────────────────────────

class PageContent(models.Model):
    """
    One editable text block on a specific page.

    Rows are pre-created by a data migration — admins simply click a row
    and edit the `value` field.  The `label` and `admin_help_text` fields
    tell the admin exactly what to write.

    In templates use:
        {% load content_tags %}
        {% get_content "home_hero_headline" as text %}
        {{ text|default:"Fallback text" }}
    """

    CONTENT_TYPE_CHOICES = [
        ("text",     "Plain text (single line)"),
        ("richtext", "Rich text (multi-paragraph)"),
    ]

    PAGE_CHOICES = [
        ("home",        "Home"),
        ("about",       "About"),
        ("contact",     "Contact"),
        ("support",     "Support Us"),
        ("partners",    "Partners"),
        ("organise",    "Organise"),
        ("contribute",  "Contribute"),
        ("resources",   "Resources"),
        ("newsletter",  "Newsletter"),
        ("faq",         "FAQ"),
        ("coc",         "Code of Conduct"),
        ("jobs",        "Jobs"),
        ("global",      "Global (all pages)"),
    ]

    page = models.CharField(
        max_length=50,
        choices=PAGE_CHOICES,
        default="home",
        db_index=True,
        help_text="Which page this content block belongs to.",
    )
    key = models.CharField(
        max_length=100,
        unique=True,
        help_text=(
            "Unique machine identifier used in templates, e.g. 'home_hero_headline'. "
            "Do not change this after creation."
        ),
    )
    label = models.CharField(
        max_length=255,
        help_text="Human-readable name shown as the field label in the admin list, e.g. 'Hero — Main Headline'.",
    )
    admin_help_text = models.CharField(
        max_length=500,
        blank=True,
        help_text=(
            "Hint shown to the admin when editing this field, "
            "e.g. 'The big bold headline over the hero image. Keep it inspiring, under 12 words.'"
        ),
    )
    value = models.TextField(
        blank=True,
        help_text="The content that will appear on the page. Leave blank to use the template default.",
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default="text",
        help_text="'Plain text' for short labels/headings; 'Rich text' for paragraphs.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["page", "key"]
        verbose_name = "Website Content"
        verbose_name_plural = "Website Content"

    def __str__(self):
        return f"[{self.get_page_display()}] {self.label}"


# ─────────────────────────────────────────────
#  WEBSITE MENU ITEMS
# ─────────────────────────────────────────────

class WebsiteMenuItem(models.Model):
    """
    A single navigation link for the header or footer.

    Header structure
    ────────────────
    • Top-level items with no `parent` render as plain links or dropdown triggers.
    • Items with a `parent` render as dropdown children.

    Footer structure
    ────────────────
    • All footer items are grouped by their `footer_column` value,
      which becomes the column heading (e.g. "Python Weekend", "Support Us").

    URL guidance
    ────────────
    Store absolute paths such as /about/ or /events/.
    Named URL patterns ({% url … %}) cannot be used here — store the resolved path instead.
    """

    POSITION_CHOICES = [
        ("header", "Header"),
        ("footer", "Footer"),
    ]

    label = models.CharField(
        max_length=100,
        help_text="Display text shown in the navigation, e.g. 'Support Us'.",
    )
    url = models.CharField(
        max_length=255,
        help_text="Absolute path, e.g. /about/ or /events/. Use / for homepage.",
    )
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="header",
        db_index=True,
        help_text="Where this item appears.",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text=(
            "Leave blank for top-level items. "
            "Set to a top-level header item to make this a dropdown child."
        ),
    )
    footer_column = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Footer only — the column heading this link belongs to, "
            "e.g. 'Python Weekend' or 'Support Us'. Leave blank for header items."
        ),
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Lower numbers appear first. Items with the same order are sorted alphabetically.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this item without deleting it.",
    )
    open_in_new_tab = models.BooleanField(
        default=False,
        help_text="Check to open this link in a new browser tab (e.g. for external links).",
    )

    class Meta:
        ordering = ["position", "order", "label"]
        verbose_name = "Website Menu"
        verbose_name_plural = "Website Menus"

    def __str__(self):
        parent_str = f" › {self.parent.label}" if self.parent_id else ""
        return f"[{self.get_position_display()}]{parent_str} {self.label}"


# ─────────────────────────────────────────────
#  FOOTER CONFIG  (singleton)
# ─────────────────────────────────────────────

class FooterConfig(models.Model):
    """
    Global footer settings — there should only ever be one row.
    Managed via the admin as a singleton (only 'Change' is exposed, never 'Add').

    If no row exists, templates fall back to hard-coded defaults.
    """
    tagline = models.CharField(
        max_length=255,
        default="Start with Python. Build with AI.",
        help_text="Short tagline shown under the Python Weekend logo in the footer.",
    )
    copyright_text = models.CharField(
        max_length=500,
        default="© {year} Python Weekend · An initiative of Code Campus International.",
        help_text=(
            "Copyright line at the bottom of every page. "
            "Use {year} as a placeholder and it will be replaced with the current year."
        ),
    )
    facebook_url  = models.URLField(blank=True, default="https://facebook.com",  help_text="Facebook page URL.")
    instagram_url = models.URLField(blank=True, default="https://instagram.com", help_text="Instagram profile URL.")
    twitter_url   = models.URLField(blank=True, default="https://x.com",         help_text="X / Twitter profile URL.")
    linkedin_url  = models.URLField(blank=True, default="https://linkedin.com",  help_text="LinkedIn page URL.")

    class Meta:
        verbose_name = "Footer Configuration"
        verbose_name_plural = "Footer Configuration"

    def __str__(self):
        return "Footer Configuration"

    def get_copyright(self):
        from django.utils import timezone
        return self.copyright_text.replace("{year}", str(timezone.now().year))


# ─────────────────────────────────────────────
#  LEGACY STUBS  (kept so existing migrations don't break; not used in templates)
# ─────────────────────────────────────────────

class WebsiteContent(models.Model):
    """Legacy stub — superseded by PageContent. Kept to avoid migration conflicts."""
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    location_identifier = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        verbose_name = "Website Content (Legacy)"
        verbose_name_plural = "Website Content (Legacy)"

    def __str__(self):
        return self.title


class WebsiteMenus(models.Model):
    """Legacy stub — superseded by WebsiteMenuItem. Kept to avoid migration conflicts."""
    POSITION_CHOICES = [
        ("header", "Header"),
        ("footer", "Footer"),
        ("sidebar", "Sidebar"),
    ]
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default="header")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        verbose_name = "Website Menu (Legacy)"
        verbose_name_plural = "Website Menus (Legacy)"

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

    @property
    def name(self):
        return self.sponsor.name if self.sponsor else ""

    @property
    def logo(self):
        return self.sponsor.logo if self.sponsor else None

    @property
    def website(self):
        return self.sponsor.website if self.sponsor else ""
