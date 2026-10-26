import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.csrf import csrf_failure as default_csrf_failure
from django.views.decorators.http import require_POST

from .forms import MemberCreationForm
from .models import VolunteerRegistration

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
    "Patron", "Deputy Patron", "Secretary", "Mobilization / Organizing",
    "Communications / Digital", "Youth Groups Lead", "Women Groups Lead",
    "Finance / Resources", "Research / Data", "Discipline / Ethics",
    "Special Programmes / Stakeholder Relations",
]

REGIONAL_LEADERSHIP = [
    "Patron", "Deputy Patron", "Secretary", "Mobilization / Organizing",
    "Communications / Digital", "Youth Groups Lead", "Women Groups Lead",
    "Finance / Resources", "Research / Data", "Discipline / Ethics",
    "Special Programmes / Stakeholder Relations",
]

COUNTY_LEADERSHIP = [
    "Patron", "Deputy Patron", "Secretary", "Mobilization / Organizing",
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
        "image": "images/boaz-nyambune-national-chair.jpeg",
        "name": "Boaz Nyambune",
        "role": "National Chair",
    },
    {
        "image": "images/kimani-w-brian-national-secretary.jpeg",
        "name": "Kimani W. Brian",
        "role": "National Secretary",
    },
    {
        "image": "images/joseph-masini-national-coordinator.jpeg",
        "name": "Joseph Masini",
        "role": "National Coordinator",
    },
    {
        "image": "images/rob-jilo-national-finance-resource-mobilization.jpeg",
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
        return redirect("home")

    return render(request, "register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "profile.html", {"profile": request.user.member_profile})


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

    aliases = {
        "full_name": ("fullName", "full_name"),
        "phone_number": ("phoneNumber", "phone_number"),
        "county": ("county",),
        "interest": ("interest",),
        "email": ("email",),
    }
    data = {}
    for field_name, keys in aliases.items():
        value = next((payload[key] for key in keys if key in payload), "")
        if not isinstance(value, str):
            return JsonResponse({"message": f"{field_name} must be a string"}, status=400)
        data[field_name] = value.strip()

    for field_name in ("full_name", "phone_number", "county", "interest"):
        if not data[field_name]:
            return JsonResponse({"message": f"{field_name} is required"}, status=400)

    limits = {"full_name": 150, "phone_number": 32, "county": 80, "interest": 80}
    for field_name, limit in limits.items():
        if len(data[field_name]) > limit:
            return JsonResponse({"message": f"{field_name} must be {limit} characters or fewer"}, status=400)

    if data["email"]:
        try:
            validate_email(data["email"])
        except ValidationError:
            return JsonResponse({"message": "Enter a valid email address"}, status=400)

    registration = VolunteerRegistration.objects.create(**data)
    return JsonResponse({
        "message": "Thank you for registering as an M4C volunteer.",
        "registration_id": registration.pk,
    }, status=201)
