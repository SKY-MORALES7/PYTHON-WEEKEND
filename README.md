# Python Weekend

Python Weekend is an open-source web platform for organizing, managing, and hosting community Python workshops and tech events. It provides end-to-end tooling for event management, participant applications, organizer onboarding, sponsor management, and educational resources.

---

## Key Features

### 1. Events & Workshop Management
- **Workshops Directory & Detail Pages**: Showcase event schedules, speaker coaches, local sponsors, venue maps, and FAQ sections.
- **Interactive Event Map & iCal Feeds**: Discover upcoming workshops globally with GPS coordinates and subscribe via `.ics` calendar feeds.
- **Target Attendee Progress Tracking**: Track applicant targets vs. actual attendees with real-time progress calculations.

### 2. Applications & Organizer Workflow
- **Attendee Applications**: Customizable dynamic application forms linked to specific workshops. Attendees can submit applications with question responses stored for review.
- **Organizer Applications**: Prospective organizers can submit workshop proposals including venue details, dates, and team members.
- **Automated Workshop Onboarding**: Approving an organizer application automatically provisions the workshop event, assigns permissions, creates or updates organizer accounts, and sends welcome credentials.
- **Co-Organizer Support**: Handles primary lead organizers and secondary co-organizers with dedicated email notifications and role-scoped permissions.

### 3. Role-Based Admin Dashboard
- **Super Admin Overview**: Complete platform visibility, organizer application approvals, team member rosters, and event application tracking ordered newest-first.
- **Organizer Admin Access**: Scoped view allowing organizers to manage only their own events and attendee applications.
- **Interactive Event Applications Hub**:
  - Grouped overview by workshop with target capacity progress bars and status breakdown (Approved, Pending, Rejected).
  - Live status indicators: **Upcoming** (green) and **Passed** (grayed out) based on event dates.
  - Hover previews of applicant answers directly from the list view.
  - One-click applicant status updates (Approve / Reject) with confirmation protection.

### 4. Community & Content
- **Tutorials & Resources**: Structured learning paths and programming articles with syntax highlighting.
- **Blog & News**: Announcements and updates for the developer community.
- **Coach & Sponsor Directories**: Highlight mentors, coaches, and supporting partner organizations.
- **Newsletter & Notifications**: Subscriber management with secure token-based unsubscribe workflows and transactional emails delivered via the Resend API (HTTP port 443).
- **Legal & Flatpages**: Terms of Service, Privacy Policy, and Code of Conduct pages with protected admin content.

---

## Tech Stack

- **Backend**: Python 3.12+, Django 5.x
- **Frontend**: Bootstrap 5.3 + Custom CSS theme, Tailwind CSS utilities
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Email Delivery**: Resend HTTPS REST API (bypasses cloud SMTP port restrictions)
- **Static Asset Management**: WhiteNoise
- **Configuration**: `python-decouple` (`.env`)

---

## Project Structure

```
PYTHON-WEEKEND/
├── applications/        # Dynamic application forms, attendee apps, organizer applications
├── coach/               # Coach and mentor profiles
├── content/             # Events, workshops, blog posts, and calendar feeds
├── core/                # Core views (Home, About, Contact, Code of Conduct), security, email
├── newsletter/          # Newsletter subscription & unsubscribe workflows
├── sponsors/            # Sponsor profiles & event partner associations
├── subscribers/         # Community subscriber models & management
├── tutorials/           # Educational tutorials and resource guides
├── templates/           # Custom Django HTML templates (including custom admin overrides)
├── static/              # CSS stylesheets, JavaScript files, images, and brand assets
├── pythonweekend/       # Django project configuration (settings, URLs, WSGI/ASGI)
├── manage.py
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/SKY-MORALES7/PYTHON-WEEKEND.git
cd PYTHON-WEEKEND

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate       # Windows PowerShell / CMD
# source venv/bin/activate  # macOS / Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```ini
DEBUG=True
SECRET_KEY=your-secret-django-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
RESEND_API_KEY=re_your_api_key_here
DEFAULT_FROM_EMAIL=Python Weekend <noreply@pythonweekend.org>
```

### 4. Run Migrations & Seed Content

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Core URL Routes

| Path | Description |
|------|-------------|
| `/` | Landing page featuring active workshops, stats, and testimonials |
| `/events/` | Workshop directory and details |
| `/events/map/` | Interactive global map of workshops |
| `/events/ical/` | iCal calendar feed subscription |
| `/organize/` | Organizer application form |
| `/coaches/` | Community coaches directory |
| `/sponsors/` | Community sponsors directory |
| `/resources/` | Tutorials and educational articles |
| `/blog/` | Community announcements and blog |
| `/code-of-conduct/` | Community Code of Conduct |
| `/admin/` | Admin & Organizer Management Dashboard |

---

## License

This project is open-source under the [MIT License](LICENSE).
