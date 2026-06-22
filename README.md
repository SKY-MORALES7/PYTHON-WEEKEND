# Python Weekend

A Django learning demo with tutorials and a blog. The **layout follows [Django Girls](https://djangogirls.org/en/)** (Bootstrap navbar, hero with workshop photo, section structure, footer columns). **Colors use the Python Weekend shield palette** — red `#E23636`, navy `#1A2F4B`, ice `#38BDF8`, and tactical dark backgrounds — not Django Girls orange.

This project is **not** affiliated with Django Girls. Branding in the nav is **Python Weekend**; the footer notes the design reference.

## Tech Stack

- **Python 3.12+**
- **Django 5.x**
- **Bootstrap 5.3** (CDN) + custom `static/css/djangogirls-theme.css`
- **SQLite** (development)
- **python-decouple** (`.env`)
- **Highlight.js** for code blocks in articles

Optional: `package.json` / Tailwind remain in the repo if you want to experiment; the default UI does **not** depend on a Tailwind build.

## Project Structure

```
PYTHON-WEEKEND/
├── manage.py
├── requirements.txt
├── pythonweekend/
├── weekend/
├── templates/
│   ├── base.html
│   ├── 404.html
│   ├── components/          # navbar, footer
│   └── weekend/
├── static/
│   ├── css/djangogirls-theme.css
│   ├── img/dg-style/hero-bg.jpg   # workshop hero (from djangogirls.org static)
│   └── js/main.js
└── README.md
```

## Quick Start

```bash
cd PYTHON-WEEKEND
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_content
python manage.py runserver
```

Open **http://127.0.0.1:8000/**

## Pages

| URL | Page |
|-----|------|
| `/` | Home (Django Girls–style sections) |
| `/tutorials/` | Tutorial list |
| `/tutorials/<slug>/` | Tutorial detail |
| `/blog/` | Blog list |
| `/blog/<slug>/` | Blog detail |
| `/about/` | About (design attribution) |
| `/contact/` | Contact form |

## Production

Set `DEBUG=False`, configure `ALLOWED_HOSTS`, run `collectstatic`. The hero image is served from your `static/` files.

## License

MIT. Respect [Django Girls](https://djangogirls.org/) trademarks and assets in your own deployments; this demo uses their public workshop photo URL only as a downloaded static file for local fidelity—replace with your own imagery if you ship a public product.
