import json
import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.csrf import csrf_failure as default_csrf_failure
from django.views.decorators.http import require_POST

from .forms import MemberCreationForm
from .models import VerificationCode
from .verification import VerificationError, issue_verification_code, verify_code

logger = logging.getLogger(__name__)

COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita-Taveta", "Garissa", "Wajir", "Mandera", "Marsabit",
    "Isiolo", "Meru", "Tharaka-Nithi", "Embu", "Kitui", "Machakos", "Makueni", "Nyandarua", "Nyeri", "Kirinyaga",
    "Murang'a", "Kiambu", "Turkana", "West Pokot", "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo-Marakwet",
    "Nandi", "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado", "Kericho", "Bomet", "Kakamega", "Vihiga",
    "Bungoma", "Busia", "Siaya", "Kisumu", "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi",
]

VALUES = [
    ("Peace", "Promoting peaceful coexistence and non-violent approaches.", "✧", "blue"),
    ("Unity", "Bringing people and communities together around shared aspirations.", "◎", "yellow"),
    ("Integrity", "Upholding honesty, accountability and ethical conduct.", "✓", "green"),
    ("Respect", "Recognizing the dignity, rights and perspectives of every person.", "♡", "red"),
    ("Inclusivity", "Creating space for people from diverse backgrounds to participate.", "◈", "teal"),
    ("Dialogue", "Encouraging communication, listening and constructive engagement.", "↔", "blue"),
    ("Service", "Putting communities and the common good at the heart of our work.", "→", "yellow"),
]

STATS = [
    ("1000+", "Peace Ambassadors", "🕊️"),
    ("47", "Counties Engaged", "🗺️"),
    ("15K+", "Citizens Mobilized", "👥"),
    ("500+", "Community Leaders", "🎯"),
]

NATIONAL_LEADERSHIP = [
    "National Patron", "Deputy Patron", "Secretary", "Mobilization / Organizing",
    "Communications / Digital", "Youth Groups Lead", "Women Groups Lead",
    "Finance / Resources", "Research / Data", "Discipline / Ethics",
    "Special Programmes / Stakeholder Relations",
]

REGIONAL_LEADERSHIP = [
    "Regional Patron", "Deputy Patron", "Secretary", "Mobilization / Organizing",
    "Communications / Digital", "Youth Groups Lead", "Women Groups Lead",
    "Finance / Resources", "Research / Data", "Discipline / Ethics",
    "Special Programmes / Stakeholder Relations",
]

COUNTY_LEADERSHIP = [
    "County Patron", "Deputy Patron", "Secretary", "Mobilization / Organizing",
    "Communications / Digital", "Youth Groups Lead", "Women Groups Lead",
    "Finance / Resources", "Research / Data", "Discipline / Ethics",
    "Special Programmes / Stakeholder Relations",
]

COMRADES_ROLES = [
    "Campus Patron", "Campus Chairperson", "Deputy Chairperson", "Secretary",
    "Organizing Secretary", "Treasurer", "Communications / Digital Lead",
    "Academic & Policy Lead", "Welfare & Inclusion Lead", "Mobilization Team",
    "Class / Department Ambassadors",
]

LEADERSHIP_PROFILES = [
    {
        "image": "images/National_chair_chief.jpeg",
        "name": "",
        "role": "National Chair",
    },
    {
        "image": "images/Kimani_w_Brian_National_secretary.jpeg",
        "name": "Kimani W. Brian",
        "role": "National Secretary",
    },
    {
        "image": "images/Joseph_masini_National_coodinater.jpeg",
        "name": "Joseph Masini",
        "role": "National Coordinator",
    },
    {
        "image": "images/[1201 PM, 1072026]National finance and resource mobilization  Rob Jillo.jpeg",
        "name": "Rob Jilo",
        "role": "National Finance & Resource Mobilization",
    },
    {
        "image": "images/Jared_opiyo_National_operations.jpeg",
        "name": "Jared Opiyo",
        "role": "National Operations",
    },
    {
        "image": "images/Muchina_nyaga_National_media_and_communication.jpeg",
        "name": "Muchina Nyaga",
        "role": "National Media and Communication",
    },
]

COUNTY_DIRECTORY_PATH = Path(settings.BASE_DIR) / "static" / "data" / "kenya-county-directory.json"
COUNTY_DIRECTORY = json.loads(COUNTY_DIRECTORY_PATH.read_text(encoding="utf-8"))["counties"]


def make_county_profiles():
    profiles = []
    for county in COUNTIES:
        directory = COUNTY_DIRECTORY[county]
        profiles.append({
            "name": county,
            "slug": directory["slug"],
            "region": "National county network",
            "county_patron": "County Patron to be confirmed",
            "ward_leadership": "Ward leadership structure under development",
            "focus": "Peacebuilding, outreach and mobilization",
            "subcounties": directory["subcounties"],
            "ward_count": sum(len(subcounty["wards"]) for subcounty in directory["subcounties"]),
        })
    return profiles

COUNTY_PROFILES = make_county_profiles()


def home(request):
    return render(request, "index.html", {
        "counties": COUNTIES,
        "values": VALUES,
        "stats": STATS,
    })


def leadership(request):
    return render(request, "leadership.html", {
        "leadership_profiles": LEADERSHIP_PROFILES,
        "national_leadership": NATIONAL_LEADERSHIP,
        "regional_leadership": REGIONAL_LEADERSHIP,
        "county_leadership": COUNTY_LEADERSHIP,
    })


def comrades(request):
    return render(request, "comrades.html", {
        "campus_roles": COMRADES_ROLES,
    })


def counties(request):
    return render(request, "counties.html", {
        "counties": COUNTY_PROFILES,
    })


def county_detail(request, slug):
    county = next((item for item in COUNTY_PROFILES if item["slug"] == slug), None)
    if county is None:
        return render(request, "county_detail.html", {
            "county": {"name": "County", "description": "County profile not yet available."},
        }, status=404)
    return render(request, "county_detail.html", {"county": county})


class MemberLoginView(LoginView):
    template_name = "login.html"

def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = MemberCreationForm(request.POST or None)
    form.fields["county"].choices = [("", "Select county")] + [(county, county) for county in COUNTIES]
    for field_name, autocomplete in (
        ("full_name", "name"),
        ("username", "username"),
        ("email", "email"),
        ("phone_number", "tel"),
        ("password1", "new-password"),
        ("password2", "new-password"),
    ):
        form.fields[field_name].widget.attrs.update({
            "autocomplete": autocomplete,
            "aria-invalid": "true" if form[field_name].errors else "false",
        })

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        is_secure_deployment = (
            request.is_secure() or request.META.get("HTTP_X_FORWARDED_PROTO") == "https"
        ) and request.get_host().endswith("onrender.com")
        return redirect("verify-account" if is_secure_deployment else "home")

    return render(request, "register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "profile.html", {"profile": request.user.member_profile})


@login_required
def verify_account(request):
    profile = request.user.member_profile
    if request.method == "POST":
        channel_value = request.POST.get("channel", "")
        action = request.POST.get("action", "")
        channel = VerificationCode.Channel(channel_value) if channel_value in {"email", "phone"} else None

        if action == "resend" and channel is not None:
            try:
                issue_verification_code(request.user, channel, request=request)
            except VerificationError as exc:
                messages.error(request, str(exc))
            else:
                messages.success(request, f"A new {channel.label.lower()} verification code has been sent.")
            return redirect("verify-account")

        if action == "verify" and channel is not None:
            code = (request.POST.get("code") or "").strip()
            if not code:
                messages.error(request, "Enter the 6-digit code from your message.")
            else:
                ok, message = verify_code(request.user, channel, code)
                if ok:
                    messages.success(request, message)
                else:
                    messages.error(request, message)
            return redirect("verify-account")

        messages.error(request, "That verification request could not be processed.")
        return redirect("verify-account")

    return render(request, "verify_account.html", {"profile": profile})


def csrf_failure(request, reason=""):
    if request.path == "/api/volunteers":
        return JsonResponse(
            {"message": "Your form security token expired. Reload the page and try again."},
            status=403,
        )
    return default_csrf_failure(request, reason=reason)


@require_POST
def volunteer_registration(request):
    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"message": "Invalid JSON"}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"message": "Invalid request body"}, status=400)

    field_names = ("fullName", "phoneNumber", "county", "interest", "email")
    data = {
        name: payload.get(name, "").strip() if isinstance(payload.get(name, ""), str) else ""
        for name in field_names
    }

    if any(not data[name] for name in field_names[:4]):
        return JsonResponse({"message": "Missing required fields"}, status=400)

    logger.info("New volunteer registration: %s", data)
    return JsonResponse({
        "message": "Thank you! Welcome to M4C. Check your WhatsApp for next steps!",
        "data": data,
    })
