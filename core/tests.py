from unittest.mock import patch

from django.test import TestCase, override_settings

from core.utils import send_newsletter_welcome


class NewsletterEmailTests(TestCase):
    @override_settings(EMAIL_ENABLED=True, EMAIL_HOST_PASSWORD="")
    @patch("threading.Thread")
    def test_send_newsletter_welcome_skips_when_email_not_configured(self, mock_thread):
        send_newsletter_welcome("user@example.com")
        mock_thread.assert_not_called()

    @override_settings(EMAIL_ENABLED=True, EMAIL_HOST_PASSWORD="secret")
    @patch("threading.Thread")
    def test_send_newsletter_welcome_queues_background_send(self, mock_thread):
        send_newsletter_welcome("user@example.com")
        mock_thread.assert_called_once()
        self.assertTrue(mock_thread.call_args.kwargs["daemon"])


class NewsletterUnsubscribeTests(TestCase):
    def setUp(self):
        from subscribers.models import Subscriber
        self.sub = Subscriber.objects.create(email="reader@example.com", is_active=True)

    def test_unsubscribe_via_token_link(self):
        from core.utils import get_unsubscribe_url
        unsub_url = get_unsubscribe_url(self.sub.email)
        token = unsub_url.split("/unsubscribe/")[1].strip("/")

        response = self.client.get(f"/newsletter/unsubscribe/{token}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have been unsubscribed")

        self.sub.refresh_from_db()
        self.assertFalse(self.sub.is_active)

    def test_resubscribe_reactivates_inactive_subscriber(self):
        self.sub.is_active = False
        self.sub.save()

        with patch("core.views.send_newsletter_welcome") as mock_welcome:
            response = self.client.post("/newsletter/", {"email": "reader@example.com"})
            self.assertEqual(response.status_code, 302)
            mock_welcome.assert_called_once()

        self.sub.refresh_from_db()
        self.assertTrue(self.sub.is_active)

    def test_manual_unsubscribe_form(self):
        response = self.client.post("/newsletter/unsubscribe/", {"email": "reader@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have been unsubscribed")

        self.sub.refresh_from_db()
        self.assertFalse(self.sub.is_active)


class ContactNotificationTests(TestCase):
    @patch("core.utils.send_resend_email")
    def test_contact_form_delivers_acknowledgment_and_staff_alert(self, mock_send):
        from core.models import ContactMessage
        from core.utils import _deliver_contact_notifications

        _deliver_contact_notifications("Jane Doe", "jane@example.com", "coach", "I want to coach.")
        # Expect at least 2 emails sent: one to submitter, one to staff
        self.assertGreaterEqual(mock_send.call_count, 2)
        submitter_call = mock_send.call_args_list[0]
        self.assertIn("jane@example.com", submitter_call.kwargs["recipient_list"])

