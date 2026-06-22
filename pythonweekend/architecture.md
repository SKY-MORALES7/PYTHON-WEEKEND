Architecture
SUPER ADMIN (You)
        │
        ▼
Review Applications
        │
        ▼
Approve Event Organizers
        │
        ▼
Create Organizer Admin Accounts
        │
        ▼
Send Login Credentials
        │
        ▼
Organizer Admin Dashboard
Step 1: Create Your Super Admin

Since you're the owner of the platform, you need exactly one account with complete access.

Run:

python manage.py createsuperuser

Example:

Username: kenter
Email: you@example.com
Password: ********

This account can:

✅ Approve applications

✅ Create organizer admins

✅ Manage all events

✅ Manage users

✅ Manage permissions

✅ Delete anything

Step 2: Create an Organizer Group

Instead of manually assigning permissions to every organizer.

Create a Group:

Organizer

Permissions:

Can add Event
Can change Event

Can add Coach
Can change Coach

Can add Sponsor
Can change Sponsor

Can add Website Content
Can change Website Content

Can add Menu
Can change Menu

Do NOT give:

User Management
Groups
Permissions
Step 3: Application System

Applicant fills:

Name
Email
Country
City
Why do you want to host Python Weekend?
Experience
Expected attendees

Stored in:

class EventApplication(models.Model):
    ...

Status:

Pending
Approved
Rejected
Step 4: Super Admin Reviews Applications

Dashboard:

Applications

[Approve]
[Reject]

When approved:

Application
     ↓
Create Event
     ↓
Create Organizer Account
     ↓
Assign Organizer Group
     ↓
Send Email
Step 5: Create Organizer Account Automatically

When approved:

user = User.objects.create_user(
    username="pythonweekend_lagos",
    password=temp_password,
)

Assign:

user.groups.add(organizer_group)
Step 6: Email Organizer

Example:

Subject: Python Weekend Organizer Account

Hello John,

Your application has been approved.

Username:
pythonweekend_lagos

Password:
X7f!9Kz2

Login:
https://pythonweekend.org/admin

Please change your password after first login.
Step 7: Organizer Dashboard

Their admin should look similar to your Django Girls screenshot.

EVENTS
    Event Details

COACHES
    Coaches

SPONSORS
    Sponsors

CONTENT
    Website Content
    Menus

APPLICATIONS
    Participants

They should NOT see:

Users
Groups
Permissions
Step 8: Organizer Manages Their Event

They can:

Add Coaches
Add Sponsors
Update Schedule
Update Venue
Manage Website Content
View Applicants

But only for THEIR event.

Not every event.

Step 9: Long-Term Structure

Eventually:

SUPER ADMIN
    │
    ├── Lagos Organizer
    │       └── Lagos Event
    │
    ├── Abuja Organizer
    │       └── Abuja Event
    │
    ├── Kano Organizer
    │       └── Kano Event
    │
    └── Port Harcourt Organizer
            └── Port Harcourt Event

One platform.

Many events.

Each organizer only sees their own event.

Your Immediate Next Steps

I would do them in this order:

Phase 1
✓ Create superuser
✓ Create Event model
✓ Create Coach model
✓ Create Sponsor model
✓ Register in Django Admin
Phase 2
✓ Create EventApplication model
✓ Build application form
✓ Store applications
Phase 3
✓ Create Organizer Group
✓ Configure permissions
✓ Create organizer accounts
Phase 4
✓ Automatic approval workflow
✓ Email credentials
✓ Organizer-specific dashboard

If you follow this order, you'll end up with almost the same workflow Django Girls uses, but adapted for Python Weekend.