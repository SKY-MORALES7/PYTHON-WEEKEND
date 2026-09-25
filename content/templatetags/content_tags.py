"""
content_tags
────────────
Custom template tags for the content app.

Usage in templates:

    {% load content_tags %}

    {# Fetch a page content value by key #}
    {% get_content "home_hero_headline" as hero_text %}
    <h1>{{ hero_text|default:"We inspire everyone to fall in love with programming." }}</h1>

    {# Fetch top-level menu items for a position (with children pre-fetched) #}
    {% get_menu "header" as header_menu %}
    {% for item in header_menu %}
      ...
    {% endfor %}

    {# Fetch the footer config singleton #}
    {% get_footer_config as footer_cfg %}
    <p>{{ footer_cfg.tagline }}</p>
"""

from django import template
from django.core.cache import cache
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def linkify_codecampus(value, custom_url=None):
    """
    Replace the plain text 'Code Campus' in a copyright string with a
    clickable link to the official site. The URL can be passed dynamically.
    Output is marked safe so the anchor tag renders correctly.
    """
    safe_value = escape(value)
    url = custom_url if custom_url else "https://codecampus.com.ng/"
    link = (
        f'<a href="{escape(url)}" target="_blank" rel="noopener" '
        'class="hover:text-shield-ice transition-colors">Code Campus</a>'
    )
    return mark_safe(safe_value.replace("Code Campus", link))

# ─── helpers ─────────────────────────────────────────────────────────────────

def _get_content_map():
    """
    Return a dict of {key: value} for all PageContent rows, cached for 5 min.
    Cache is invalidated whenever a PageContent row is saved (via the admin
    save hook in admin.py).
    """
    cached = cache.get("site_page_content_map")
    if cached is not None:
        return cached
    try:
        from content.models import PageContent
        mapping = {row.key: row.value for row in PageContent.objects.all()}
    except Exception:
        mapping = {}
    cache.set("site_page_content_map", mapping, 300)  # 5 minutes
    return mapping


class MenuItemFallback:
    def __init__(self, label, url, child_items=None, open_in_new_tab=False):
        self.label = label
        self.url = url
        self.child_items = child_items or []
        self.open_in_new_tab = open_in_new_tab


def _get_default_header_menu():
    return [
        MenuItemFallback("Support Us", "#", [
            MenuItemFallback("Support a Workshop", "/support/"),
            MenuItemFallback("Our Partners", "/partners/"),
            MenuItemFallback("Corporate Sponsorships", "/sponsors/"),
        ]),
        MenuItemFallback("Volunteer", "#", [
            MenuItemFallback("Organise a Workshop", "/applications/organize/"),
            MenuItemFallback("Become a Coach", "/coaches/"),
            MenuItemFallback("Contribute", "/contribute/"),
        ]),
        MenuItemFallback("Resources", "/resources/"),
        MenuItemFallback("Events", "/events/"),
        MenuItemFallback("What's New?", "#", [
            MenuItemFallback("Our Blog", "/content/blog/"),
            MenuItemFallback("Newsletter", "/newsletter/"),
        ]),
        MenuItemFallback("Contact Us", "/contact/"),
    ]


def _seed_header_menu_items_to_db():
    try:
        from content.models import WebsiteMenuItem
        if WebsiteMenuItem.objects.filter(position="header").exists():
            return
        s1 = WebsiteMenuItem.objects.create(label="Support Us", url="#", position="header", order=1)
        WebsiteMenuItem.objects.create(label="Support a Workshop", url="/support/", position="header", order=1, parent=s1)
        WebsiteMenuItem.objects.create(label="Our Partners", url="/partners/", position="header", order=2, parent=s1)
        WebsiteMenuItem.objects.create(label="Corporate Sponsorships", url="/sponsors/", position="header", order=3, parent=s1)

        s2 = WebsiteMenuItem.objects.create(label="Volunteer", url="#", position="header", order=2)
        WebsiteMenuItem.objects.create(label="Organise a Workshop", url="/applications/organize/", position="header", order=1, parent=s2)
        WebsiteMenuItem.objects.create(label="Become a Coach", url="/coaches/", position="header", order=2, parent=s2)
        WebsiteMenuItem.objects.create(label="Contribute", url="/contribute/", position="header", order=3, parent=s2)

        WebsiteMenuItem.objects.create(label="Resources", url="/resources/", position="header", order=3)
        WebsiteMenuItem.objects.create(label="Events", url="/events/", position="header", order=4)

        s5 = WebsiteMenuItem.objects.create(label="What's New?", url="#", position="header", order=5)
        WebsiteMenuItem.objects.create(label="Our Blog", url="/content/blog/", position="header", order=1, parent=s5)
        WebsiteMenuItem.objects.create(label="Newsletter", url="/newsletter/", position="header", order=2, parent=s5)

        WebsiteMenuItem.objects.create(label="Contact Us", url="/contact/", position="header", order=6)
    except Exception:
        pass


def _get_menu_items(position):
    """
    Return top-level active menu items for `position`, each with its active
    children pre-loaded as a list attached to `.child_items`.
    Cached per position for 5 minutes.
    """
    cache_key = f"site_menu_{position}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        from content.models import WebsiteMenuItem
        top_level = list(
            WebsiteMenuItem.objects.filter(
                position=position,
                parent__isnull=True,
                is_active=True,
            ).order_by("order", "label")
        )
        if not top_level and position == "header":
            _seed_header_menu_items_to_db()
            top_level = list(
                WebsiteMenuItem.objects.filter(
                    position=position,
                    parent__isnull=True,
                    is_active=True,
                ).order_by("order", "label")
            )

        # Attach children to each top-level item
        if top_level:
            all_children = WebsiteMenuItem.objects.filter(
                position=position,
                parent__in=top_level,
                is_active=True,
            ).order_by("order", "label").select_related("parent")

            children_map = {}
            for child in all_children:
                children_map.setdefault(child.parent_id, []).append(child)

            for item in top_level:
                item.child_items = children_map.get(item.pk, [])
        result = top_level
    except Exception:
        result = []

    if not result and position == "header":
        result = _get_default_header_menu()

    try:
        cache.set(cache_key, result, 300)
    except Exception:
        pass
    return result


def _get_footer_config():
    """Return the FooterConfig singleton (or None) with 5-min caching."""
    cached = cache.get("site_footer_config")
    if cached is not None:
        return cached
    try:
        from content.models import FooterConfig
        cfg = FooterConfig.objects.first()
    except Exception:
        cfg = None
    cache.set("site_footer_config", cfg, 300)
    return cfg


# ─── template tags ────────────────────────────────────────────────────────────

@register.simple_tag
def get_content(key):
    """
    Return the PageContent value for the given key.
    If the key doesn't exist, return empty string.
    """
    from django.utils import timezone
    mapping = _get_content_map()
    val = mapping.get(key, "")
    if isinstance(val, str) and "{year}" in val:
        return val.replace("{year}", str(timezone.now().year))
    return val


@register.simple_tag
def get_menu(position):
    """
    Fetch top-level active menu items for a position ("header" or "footer").
    Each item has a `.child_items` list of its active children.

    Usage:
        {% get_menu "header" as header_menu %}
        {% for item in header_menu %}
          {{ item.label }} — children: {% for c in item.child_items %}{{ c.label }}{% endfor %}
        {% endfor %}
    """
    return _get_menu_items(position)


@register.simple_tag
def get_footer_config():
    """
    Fetch the FooterConfig singleton.

    Usage:
        {% get_footer_config as footer_cfg %}
        {{ footer_cfg.tagline }}
    """
    return _get_footer_config()


@register.simple_tag
def get_footer_columns(footer_items):
    """
    Group a list of footer menu items by their footer_column field.
    Returns a list of (column_name, [items]) tuples, preserving insertion order.

    Usage:
        {% get_menu "footer" as footer_menu %}
        {% get_footer_columns footer_menu as columns %}
        {% for col_name, col_items in columns %}
          <h4>{{ col_name }}</h4>
          {% for item in col_items %}<a href="{{ item.url }}">{{ item.label }}</a>{% endfor %}
        {% endfor %}
    """
    columns = {}
    order = []
    for item in footer_items:
        col = item.footer_column or "Other"
        if col not in columns:
            columns[col] = []
            order.append(col)
        columns[col].append(item)
    return [(col, columns[col]) for col in order]
