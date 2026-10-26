import json

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from website.models import MemberProfile, VolunteerRegistration
from website.views import COUNTY_PROFILES


class PublicPageTests(SimpleTestCase):
    def test_home_page_has_join_and_sign_in_flows(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Promoting Peace, Unity")
        self.assertContains(response, "Constructive Dialogue")
        self.assertContains(response, "m4c-logo.jpeg")
        self.assertContains(response, "hero-background-logo")
        self.assertContains(response, 'name="twitter:card" content="summary_large_image"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, 'action="/register/"')
        self.assertContains(response, 'action="/login/"')
        self.assertContains(response, 'href="tel:+254702154221"')
        self.assertContains(response, 'href="mailto:infomovementforchange.co@gmail.com"')
        self.assertContains(response, 'class="contact-buttons"')
        for field in ("full_name", "username", "county", "interest", "email", "phone_number", "password1", "password2"):
            self.assertContains(response, f'name="{field}"')
        for stock_image in ("politician-1.jpeg", "politician-2.jpeg", "politician-3.jpeg"):
            self.assertNotContains(response, stock_image)

    def test_public_routes_and_unknown_county(self):
        for route in ("home", "leadership", "comrades", "counties"):
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'class="contact-buttons"')

        county_response = self.client.get(reverse("county-detail", args=("nairobi",)))
        self.assertEqual(county_response.status_code, 200)
        self.assertContains(county_response, 'class="contact-buttons"')
        self.assertEqual(self.client.get(reverse("county-detail", args=("not-a-county",))).status_code, 404)

    def test_leadership_only_shows_confirmed_active_profiles_and_roles(self):
        response = self.client.get(reverse("leadership"))

        self.assertContains(response, "National Leadership")
        self.assertContains(response, "Regional Leadership")
        self.assertContains(response, "County Leadership")
        self.assertNotContains(response, "11 members")
        self.assertContains(response, "National Chair")
        for name in (
            "Boaz Nyambune",
            "Kimani W. Brian",
            "Joseph Masini",
            "Rob Jilo",
            "Jared Opiyo",
            "Muchina Nyaga",
        ):
            self.assertContains(response, name)
        for inactive_name in (
            "Brian Gitonga", "Martin Kor", "John Waithaka",
            "Wanjeri Esther Stacy", "Esther Muteri", "Moses Mwero",
        ):
            self.assertNotContains(response, inactive_name)
        for role in (
            "Patron", "Deputy Patron", "Secretary", "Mobilization / Organizing",
            "Communications / Digital", "Youth Groups Lead", "Women Groups Lead",
            "Finance / Resources", "Research / Data", "Discipline / Ethics",
            "Special Programmes / Stakeholder Relations",
        ):
            self.assertContains(response, role)

    def test_county_and_ward_directory_integrity(self):
        self.assertEqual(len(COUNTY_PROFILES), 47)
        self.assertEqual(sum(county["ward_count"] for county in COUNTY_PROFILES), 1450)

        wards = json.loads((settings.BASE_DIR / "static/data/kenya-wards.geojson").read_text(encoding="utf-8"))
        counties = json.loads((settings.BASE_DIR / "static/data/kenya-counties.geojson").read_text(encoding="utf-8"))
        self.assertEqual(len(wards["features"]), 1450)
        self.assertEqual(len(counties["features"]), 47)
        for feature in wards["features"]:
            self.assertTrue(feature["properties"].get("countyName"))
            self.assertTrue(feature["properties"].get("subcountyName"))
            self.assertTrue(feature["properties"].get("wardName"))

    def test_county_detail_has_real_wards_and_unconfirmed_leadership(self):
        response = self.client.get(reverse("county-detail", args=("nairobi",)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dagoretti")
        self.assertContains(response, "Mutu-ini Ward")
        self.assertContains(response, "Ward Patron to be confirmed")

    def test_comrades_page_describes_campus_roles_and_sections(self):
        response = self.client.get(reverse("comrades"))

        for text in ("Comrades", "Campus Patron", "Academic &amp; Policy Lead",
                     "Class / Department Ambassadors", "Campus Events", "Join Comrades"):
            self.assertContains(response, text)

    def test_static_files_are_configured(self):
        self.assertEqual(settings.STATIC_URL, "/static/")
        self.assertTrue(settings.STATICFILES_DIRS)
        self.assertTrue(settings.STATIC_ROOT)


class VolunteerApiTests(TestCase):
    url = reverse("volunteer-registration")

    def post_json(self, data):
        return self.client.post(self.url, json.dumps(data), content_type="application/json")

    def test_saves_camel_case_registration_and_returns_only_receipt(self):
        response = self.post_json({
            "fullName": " Amina Otieno ",
            "phoneNumber": " +254700000000 ",
            "county": " Nairobi ",
            "interest": " Youth Leader ",
            "email": " amina@example.com ",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.json()), {"message", "registration_id"})
        registration = VolunteerRegistration.objects.get(pk=response.json()["registration_id"])
        self.assertEqual(registration.full_name, "Amina Otieno")
        self.assertEqual(registration.phone_number, "+254700000000")
        self.assertEqual(registration.county, "Nairobi")
        self.assertEqual(registration.interest, "Youth Leader")
        self.assertEqual(registration.email, "amina@example.com")

    def test_accepts_snake_case_and_optional_email(self):
        response = self.post_json({
            "full_name": "Amina Otieno",
            "phone_number": "+254700000000",
            "county": "Nairobi",
            "interest": "Youth Leader",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(VolunteerRegistration.objects.get().email, "")

    def test_rejects_malformed_and_non_object_json(self):
        malformed = self.client.post(self.url, "{", content_type="application/json")
        non_object = self.post_json(["not", "an", "object"])
        self.assertEqual(malformed.status_code, 400)
        self.assertEqual(malformed.json()["message"], "Invalid JSON")
        self.assertEqual(non_object.status_code, 400)
        self.assertEqual(non_object.json()["message"], "Invalid request body")

    def test_rejects_missing_required_fields(self):
        response = self.post_json({"fullName": "Amina"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("required", response.json()["message"])

    def test_rejects_excessive_lengths_and_invalid_email(self):
        data = {
            "full_name": "A" * 151,
            "phone_number": "+254700000000",
            "county": "Nairobi",
            "interest": "Youth Leader",
        }
        too_long = self.post_json(data)
        data["full_name"] = "Amina Otieno"
        data["email"] = "not-an-email"
        invalid_email = self.post_json(data)

        self.assertEqual(too_long.status_code, 400)
        self.assertIn("150", too_long.json()["message"])
        self.assertEqual(invalid_email.status_code, 400)
        self.assertIn("email", invalid_email.json()["message"])

    def test_rejects_non_string_values(self):
        response = self.post_json({
            "fullName": "Amina",
            "phoneNumber": 254700000000,
            "county": "Nairobi",
            "interest": "Youth Leader",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("string", response.json()["message"])

    def test_only_accepts_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    @override_settings(CSRF_TRUSTED_ORIGINS=["https://localhost:8000"])
    def test_accepts_csrf_token_from_https_origin(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get(reverse("home"), HTTP_HOST="localhost:8000")
        token = page.cookies["csrftoken"].value
        response = client.post(
            self.url,
            json.dumps({
                "full_name": "Amina Otieno",
                "phone_number": "+254700000000",
                "county": "Nairobi",
                "interest": "Youth Leader",
            }),
            content_type="application/json",
            HTTP_HOST="localhost:8000",
            HTTP_ORIGIN="https://localhost:8000",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)

    def test_csrf_failure_returns_actionable_json(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("home"))
        response = client.post(
            self.url,
            json.dumps({
                "fullName": "Amina Otieno",
                "phoneNumber": "+254700000000",
                "county": "Nairobi",
                "interest": "Youth Leader",
            }),
            content_type="application/json",
            HTTP_X_CSRFTOKEN="stale-token",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["message"],
            "Your form security token expired. Reload the page and try again.",
        )


class MemberAccountTests(TestCase):
    password = "Robust-M4C-passphrase-9482!"

    def make_user(self, username="m4c-member", email="member@example.com"):
        return get_user_model().objects.create_user(
            username=username,
            email=email,
            password=self.password,
        )

    def test_registration_creates_account_and_logs_in_without_verification(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get(reverse("home"))
        token = page.cookies["csrftoken"].value
        response = client.post(reverse("register"), {
            "full_name": "New M4C Member",
            "username": "new-m4c-member",
            "email": "new-member@example.com",
            "phone_number": "0712345678",
            "county": "Nairobi",
            "interest": "Youth Leader",
            "password1": self.password,
            "password2": self.password,
        }, HTTP_X_CSRFTOKEN=token, follow=True)

        self.assertRedirects(response, reverse("home"))
        user = get_user_model().objects.get(username="new-m4c-member")
        self.assertEqual(client.session.get("_auth_user_id"), str(user.pk))
        self.assertTrue(user.check_password(self.password))
        self.assertEqual(user.member_profile.full_name, "New M4C Member")
        self.assertEqual(user.member_profile.phone_number, "+254712345678")
        self.assertEqual(user.member_profile.county, "Nairobi")
        self.assertEqual(user.member_profile.interest, "Youth Leader")
        self.assertEqual(client.get(reverse("profile")).status_code, 200)
        self.assertEqual(client.get("/verify-account/").status_code, 404)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(reverse("register"), {
            "full_name": "New M4C Member",
            "username": "new-m4c-member",
            "email": "new-member@example.com",
            "phone_number": "+254712345678",
            "county": "Nairobi",
            "interest": "Youth Leader",
            "password1": self.password,
            "password2": "Different-passphrase-8274!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].has_error("password2"))

    def test_profile_shows_account_details_without_verification_status(self):
        user = self.make_user(email="profile@example.com")
        MemberProfile.objects.create(
            user=user,
            full_name="Profile Member",
            phone_number="+254712345680",
            county="Nairobi",
            interest="Youth Leader",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        for detail in ("profile@example.com", "+254712345680", "Nairobi", "Youth Leader"):
            self.assertContains(response, detail)
        self.assertNotContains(response, "Verified")
        self.assertNotContains(response, "Pending")

    def test_login_accepts_email_address_and_logout_works(self):
        user = self.make_user()
        response = self.client.post(reverse("login"), {
            "username": "MEMBER@example.com",
            "password": self.password,
        })

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_can_manage_member_and_volunteer_records(self):
        self.assertIn(MemberProfile, admin.site._registry)
        self.assertIn(VolunteerRegistration, admin.site._registry)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="Movement for Change <noreply@movementforchange.co.ke>",
    )
    def test_password_reset_sends_branded_https_email(self):
        self.make_user(username="reset-member")
        response = self.client.post(
            reverse("password_reset"),
            {"email": "member@example.com"},
            HTTP_HOST="movementforchange.co.ke",
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["member@example.com"])
        self.assertIn("https://movementforchange.co.ke/password-reset/", mail.outbox[0].body)
