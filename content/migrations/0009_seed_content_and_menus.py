"""
0009_seed_content_and_menus.py

Data migration that pre-creates:
  1. All PageContent rows (one per editable text field on every page)
  2. All WebsiteMenuItem rows (mirroring the current hard-coded navbar + footer)
  3. One FooterConfig row with sensible defaults

Admins can immediately open Django admin → Page Content, click any row, and
edit the text without needing to know any keys or create any rows themselves.
"""

from django.db import migrations


# ─── Page Content seed data ──────────────────────────────────────────────────
# Format: (page, key, label, admin_help_text, content_type, initial_value)

PAGE_CONTENT_SEED = [
    # ── Home ──────────────────────────────────────────────────────────────────
    (
        "home", "home_hero_headline",
        "Hero — Main Headline",
        "The big bold headline over the hero image. Keep it inspiring and under 12 words.",
        "text",
        "We inspire everyone to fall in love with programming.",
    ),
    (
        "home", "home_hero_subheadline",
        "Hero — Sub Headline",
        "One or two sentences below the hero headline. Briefly describes what Python Weekend does.",
        "richtext",
        (
            "Python Weekend organises free Python & Django workshops, creates open-source "
            "online tutorials and curates amazing first experiences with technology."
        ),
    ),
    (
        "home", "home_what_is_heading",
        "\"What is Python Weekend?\" — Section Heading",
        "Section heading for the 'What is Python Weekend?' block. Defaults to that phrase.",
        "text",
        "What is Python Weekend?",
    ),
    (
        "home", "home_what_is_body",
        "\"What is Python Weekend?\" — Body",
        (
            "Main description of Python Weekend shown to the left of the video on the home page. "
            "Explain what the initiative is, who runs it, and what happens at events. "
            "You can use line breaks to separate paragraphs."
        ),
        "richtext",
        (
            "Python Weekend is a community-driven initiative that empowers and helps anyone "
            "organise free, hands-on programming workshops by providing tools, resources and "
            "support. We are a volunteer-run community with coaches contributing to bring more "
            "amazing people into the world of technology. We are making technology more "
            "approachable by creating resources designed with empathy.\n\n"
            "During each of our events, participants build their first web application using "
            "HTML, CSS, Python and Django — in just one weekend."
        ),
    ),
    (
        "home", "home_impact_heading",
        "Impact Section — Heading",
        "Heading for the impact statistics section, e.g. 'Python Weekend impact'.",
        "text",
        "Python Weekend impact",
    ),
    (
        "home", "home_bring_pw_heading",
        "Bring PW to Your City — Heading",
        "Heading for the 'Bring Python Weekend to your city!' section.",
        "text",
        "Bring Python Weekend to your city!",
    ),
    (
        "home", "home_bring_pw_body",
        "Bring PW to Your City — Body",
        (
            "Paragraph explaining how someone can bring Python Weekend to their city. "
            "Mention the curriculum, tools, and community support provided."
        ),
        "richtext",
        (
            "Is there no Python Weekend event in your city? You can help make it happen! "
            "We provide the curriculum, tools, and a supportive community of organisers "
            "all over the world."
        ),
    ),
    (
        "home", "home_coaches_heading",
        "Coaches Spotlight — Heading",
        "Heading above the coaches spotlight grid, e.g. 'Python Weekend Coaches'.",
        "text",
        "Python Weekend Coaches",
    ),
    (
        "home", "home_coaches_intro",
        "Coaches Spotlight — Intro",
        "One sentence shown above the coach cards, introducing the spotlight.",
        "text",
        "Each week we try to introduce one amazing coach who uses Python or Django and highlight their work:",
    ),
    (
        "home", "home_blog_heading",
        "Latest Blog — Heading",
        "Heading above the latest blog posts, e.g. 'Latest from our blog'.",
        "text",
        "Latest from our blog",
    ),
    (
        "home", "home_support_heading",
        "Support Our Work — Heading",
        "Heading of the 'Support our work' section on the home page.",
        "text",
        "Support our work",
    ),
    (
        "home", "home_support_body",
        "Support Our Work — Body",
        "Short paragraph explaining why donations or support are needed.",
        "richtext",
        "Python Weekend is a volunteer-run organisation, and we depend on your support to make it happen.",
    ),
    (
        "home", "home_newsletter_heading",
        "Stay Up To Date — Heading",
        "Heading above the newsletter sign-up form.",
        "text",
        "Stay up to date!",
    ),
    (
        "home", "home_newsletter_body",
        "Stay Up To Date — Body",
        "One or two sentences above the email input encouraging newsletter sign-up.",
        "richtext",
        (
            "Subscribe to Python Weekend Dispatch to receive the latest and greatest from our "
            "community every two weeks, straight to your inbox!"
        ),
    ),
    (
        "home", "home_community_heading",
        "Community Section — Heading",
        "Heading for the 'Check out our community!' block.",
        "text",
        "Check out our community!",
    ),
    (
        "home", "home_community_body",
        "Community Section — Body",
        "Short paragraph encouraging visitors to explore coaches and the blog.",
        "richtext",
        (
            "We have an amazing community of coaches, organisers and alumni who continue "
            "building after each workshop. Check out our coaches and blog to stay connected."
        ),
    ),
    # ── About ─────────────────────────────────────────────────────────────────
    (
        "about", "about_hero_heading",
        "Page Heading (Hero)",
        "The large H1 heading shown in the dark hero banner at the top of the About page.",
        "text",
        "About Python Weekend",
    ),
    (
        "about", "about_hero_intro",
        "Page Intro (Hero)",
        "One or two sentences shown beneath the heading in the hero banner.",
        "text",
        (
            "An initiative of Code Campus International created to make Python and artificial "
            "intelligence more approachable for complete beginners."
        ),
    ),
    (
        "about", "about_what_we_do_heading",
        "\"About Python Weekend\" — Section Heading",
        "Heading of the main 'About Python Weekend' content section.",
        "text",
        "About Python Weekend",
    ),
    (
        "about", "about_what_we_do_body",
        "\"About Python Weekend\" — Body",
        (
            "Main description. Describe what Python Weekend is, what it does, "
            "and how it came to be. Separate paragraphs with a blank line."
        ),
        "richtext",
        (
            "Python Weekend is an initiative of Code Campus International created to make "
            "Python and artificial intelligence more approachable for complete beginners.\n\n"
            "Our goal is to advance practical technology education by supporting free beginner "
            "workshops, developing accessible learning materials and helping volunteer teams "
            "create welcoming first experiences with programming.\n\n"
            "Python Weekend does this by:\n"
            "✓ Supporting free, practical Python and AI workshops\n"
            "✓ Creating beginner learning resources\n"
            "✓ Equipping local organisers and mentors\n"
            "✓ Encouraging women and underserved groups to participate in technology\n"
            "✓ Highlighting relatable Python and AI role models\n"
            "✓ Helping participants identify clear next steps after the workshop"
        ),
    ),
    (
        "about", "about_more_info_body",
        "More Information — Contact Text",
        "Short paragraph in the 'More Information' section at the bottom of the About page.",
        "richtext",
        (
            "If you would like to learn more about Python Weekend or discuss a partnership, "
            "contact us at hello@pythonweekend.org."
        ),
    ),
    # ── FAQ ───────────────────────────────────────────────────────────────────
    (
        "faq", "faq_hero_heading",
        "Page Heading (Hero)",
        "The H1 heading shown in the hero banner at the top of the FAQ page.",
        "text",
        "Frequently Asked Questions",
    ),
    (
        "faq", "faq_hero_intro",
        "Page Intro (Hero)",
        "One sentence shown beneath the FAQ page heading.",
        "text",
        "Everything you need to know about Python Weekend workshops.",
    ),
    # ── Code of Conduct ───────────────────────────────────────────────────────
    (
        "coc", "coc_hero_heading",
        "Page Heading (Hero)",
        "The H1 heading for the Code of Conduct page.",
        "text",
        "Code of Conduct",
    ),
    (
        "coc", "coc_intro",
        "Code of Conduct — Opening Paragraph",
        "The introductory paragraph shown before the list of conduct rules.",
        "richtext",
        (
            "Python Weekend is dedicated to providing a harassment-free experience for everyone, "
            "regardless of gender, gender identity and expression, age, sexual orientation, "
            "disability, physical appearance, body size, race, ethnicity, religion (or lack "
            "thereof), or technology choices."
        ),
    ),
    # ── Support Us ────────────────────────────────────────────────────────────
    (
        "support", "support_hero_heading",
        "Page Heading (Hero)",
        "The H1 heading for the Support Us page.",
        "text",
        "Support Python Weekend",
    ),
    (
        "support", "support_hero_intro",
        "Page Intro (Hero)",
        "One or two sentences beneath the Support page heading.",
        "text",
        "Help us bring free Python & AI workshops to more cities and more people.",
    ),
    # ── Organise ──────────────────────────────────────────────────────────────
    (
        "organise", "organise_hero_heading",
        "Page Heading (Hero)",
        "The H1 heading for the Organise a Workshop page.",
        "text",
        "Organise a Python Weekend",
    ),
    (
        "organise", "organise_hero_intro",
        "Page Intro (Hero)",
        "One or two sentences beneath the Organise page heading.",
        "text",
        "Bring free Python & AI workshops to your city with our support.",
    ),
    # ── Contribute ────────────────────────────────────────────────────────────
    (
        "contribute", "contribute_hero_heading",
        "Page Heading (Hero)",
        "The H1 heading for the Contribute page.",
        "text",
        "Contribute to Python Weekend",
    ),
    (
        "contribute", "contribute_hero_intro",
        "Page Intro (Hero)",
        "One or two sentences beneath the Contribute page heading.",
        "text",
        "Share your skills and help us build better resources for the whole community.",
    ),
    # ── Newsletter ────────────────────────────────────────────────────────────
    (
        "newsletter", "newsletter_hero_heading",
        "Page Heading (Hero)",
        "The H1 heading for the Newsletter page.",
        "text",
        "Python Weekend Dispatch",
    ),
    (
        "newsletter", "newsletter_hero_intro",
        "Page Intro (Hero)",
        "One or two sentences describing the newsletter, shown at the top of the page.",
        "richtext",
        (
            "Our community newsletter — packed with workshop updates, Python tips, "
            "and stories from coaches and participants around the world. Published every two weeks."
        ),
    ),
    # ── Partners ──────────────────────────────────────────────────────────────
    (
        "partners", "partners_hero_heading",
        "Page Heading (Hero)",
        "The H1 heading for the Our Partners page.",
        "text",
        "Our Partners",
    ),
    (
        "partners", "partners_hero_intro",
        "Page Intro (Hero)",
        "One or two sentences beneath the Partners page heading.",
        "text",
        "Organisations that believe in the power of community-led technology education.",
    ),
    # ── Global ────────────────────────────────────────────────────────────────
    (
        "global", "footer_tagline",
        "Footer — Tagline",
        "Short tagline shown under the Python Weekend logo in the footer on every page.",
        "text",
        "Start with Python. Build with AI.",
    ),
    (
        "global", "footer_copyright",
        "Footer — Copyright Text",
        (
            "Copyright line shown at the very bottom of every page. "
            "Use {year} as a placeholder for the current year."
        ),
        "text",
        "© {year} Python Weekend · An initiative of Code Campus International.",
    ),
]


# ─── Menu seed data ───────────────────────────────────────────────────────────
# Format: (label, url, position, parent_label_or_None, footer_column, order, open_in_new_tab)
# parent_label_or_None refers to the label of the parent item (must already exist).

MENU_SEED = [
    # ── HEADER top-level (dropdowns) ──────────────────────────────────────────
    ("Support Us",   "#", "header", None, "", 1, False),
    ("Volunteer",    "#", "header", None, "", 2, False),
    ("Resources",    "/resources/", "header", None, "", 3, False),
    ("Events",       "/events/",    "header", None, "", 4, False),
    ("What's New?",  "#", "header", None, "", 5, False),
    ("Contact Us",   "/contact/",   "header", None, "", 6, False),

    # ── HEADER children ───────────────────────────────────────────────────────
    ("Corporate Sponsorships", "/sponsors/",          "header", "Support Us",  "", 1, False),
    ("Support a Workshop",     "/support/",           "header", "Support Us",  "", 2, False),
    ("Our Partners",           "/partners/",          "header", "Support Us",  "", 3, False),
    ("Organise a Workshop",    "/apply/organise/",    "header", "Volunteer",   "", 1, False),
    ("Contribute",             "/contribute/",        "header", "Volunteer",   "", 2, False),
    ("Newsletter",             "/newsletter/",        "header", "What's New?", "", 1, False),
    ("Our Blog",               "/blog/",              "header", "What's New?", "", 2, False),

    # ── FOOTER columns ────────────────────────────────────────────────────────
    ("About",              "/about/",       "footer", None, "Python Weekend", 1, False),
    ("FAQ",                "/faq/",         "footer", None, "Python Weekend", 2, False),
    ("Newsletter",         "/newsletter/",  "footer", None, "Python Weekend", 3, False),
    ("Code of Conduct",    "/coc/",         "footer", None, "Python Weekend", 4, False),
    ("Contact",            "/contact/",     "footer", None, "Python Weekend", 5, False),

    ("Support a Workshop", "/support/",     "footer", None, "Support Us",    1, False),
    ("Contribute",         "/contribute/",  "footer", None, "Support Us",    2, False),
    ("Sponsorships",       "/sponsors/",    "footer", None, "Support Us",    3, False),
    ("Our Partners",       "/partners/",    "footer", None, "Support Us",    4, False),

    ("Python & AI Tutorial", "/resources/", "footer", None, "Resources",     1, False),
    ("Organiser's Manual",   "/resources/", "footer", None, "Resources",     2, False),
    ("Mentoring Guide",      "/resources/", "footer", None, "Resources",     3, False),
    ("Tutorial Extensions",  "/resources/", "footer", None, "Resources",     4, False),

    ("Terms & Conditions",   "/terms/",     "footer", None, "Legal",         1, False),
    ("Privacy & Cookies",    "/privacy/",   "footer", None, "Legal",         2, False),
    ("Job Board",            "/jobs/",      "footer", None, "Legal",         3, False),
]


def seed_content(apps, schema_editor):
    PageContent    = apps.get_model("content", "PageContent")
    WebsiteMenuItem = apps.get_model("content", "WebsiteMenuItem")
    FooterConfig   = apps.get_model("content", "FooterConfig")

    # 1. PageContent rows
    for page, key, label, help_text, ctype, value in PAGE_CONTENT_SEED:
        PageContent.objects.get_or_create(
            key=key,
            defaults={
                "page":            page,
                "label":           label,
                "admin_help_text": help_text,
                "content_type":    ctype,
                "value":           value,
            },
        )

    # 2. WebsiteMenuItem rows
    # First pass: create top-level items
    created_items = {}
    for label, url, position, parent_label, footer_col, order, new_tab in MENU_SEED:
        if parent_label is None:
            obj, _ = WebsiteMenuItem.objects.get_or_create(
                label=label,
                position=position,
                parent=None,
                defaults={
                    "url":           url,
                    "footer_column": footer_col,
                    "order":         order,
                    "is_active":     True,
                    "open_in_new_tab": new_tab,
                },
            )
            created_items[(label, position)] = obj

    # Second pass: create children
    for label, url, position, parent_label, footer_col, order, new_tab in MENU_SEED:
        if parent_label is not None:
            parent = created_items.get((parent_label, position))
            if parent:
                WebsiteMenuItem.objects.get_or_create(
                    label=label,
                    position=position,
                    parent=parent,
                    defaults={
                        "url":           url,
                        "footer_column": footer_col,
                        "order":         order,
                        "is_active":     True,
                        "open_in_new_tab": new_tab,
                    },
                )

    # 3. FooterConfig singleton
    FooterConfig.objects.get_or_create(
        pk=1,
        defaults={
            "tagline":       "Start with Python. Build with AI.",
            "copyright_text": "© {year} Python Weekend · An initiative of Code Campus International.",
            "facebook_url":  "https://facebook.com",
            "instagram_url": "https://instagram.com",
            "twitter_url":   "https://x.com",
            "linkedin_url":  "https://linkedin.com",
        },
    )


def unseed_content(apps, schema_editor):
    """Reverse: delete all seeded rows."""
    apps.get_model("content", "PageContent").objects.all().delete()
    apps.get_model("content", "WebsiteMenuItem").objects.all().delete()
    apps.get_model("content", "FooterConfig").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0008_pagecontent_websitemenuitem_footerconfig"),
    ]

    operations = [
        migrations.RunPython(seed_content, unseed_content),
    ]
