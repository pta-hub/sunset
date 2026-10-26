# Comprehensive AI Build Prompt — Movement for Change (M4C)

You are a senior full-stack engineer. Recreate the **Movement for Change (M4C)** website as a complete, responsive, production-conscious web application. Use the requirements below as the source of truth. Implement the complete project rather than a landing-page mockup: public information pages, Kenya county/ward directory and map, member accounts with no contact-verification step, password reset, volunteer registration API, admin integration, tests, and deployment setup.

## 1. Product purpose and audience

Build a website for **Movement for Change (M4C)**, a Kenya-wide peace, unity, community mobilization, and constructive-dialogue movement. It should present the organization's mission and values, leadership structures, campus/community participation, and its geographic presence across all 47 Kenyan counties and 1,450 mapped wards. It should allow interested people to register as volunteers and members to create accounts, sign in immediately without email or phone verification, reset passwords, and view a profile.

The site is primarily English-language and uses **Africa/Nairobi** as its time zone. Use the supplied M4C logo, leadership photographs, county directory JSON, county GeoJSON, and ward GeoJSON assets when rebuilding. Preserve actual names and titles only where present in the source data; do not invent unconfirmed leadership assignments.

## 2. Technology and architecture

- Backend: Python and Django (requirements allow Django `>=5.2,<7.0`).
- Serving: Django WSGI application, optionally served through Tornado (`tornado>=6.4,<7.0`) by `run_tornado.py`; Django development server is also supported.
- Database: SQLite for local development by default; PostgreSQL when `DATABASE_URL` is configured, using `dj-database-url` and `psycopg[binary]`.
- Static assets: Django staticfiles plus WhiteNoise middleware.
- Frontend: Django server-rendered templates, semantic HTML, custom CSS, and vanilla JavaScript. Do not replace it with an unrelated frontend framework unless explicitly asked.
- Main project package: `m4c/` (`settings.py`, `urls.py`, `wsgi.py`). Main application: `website/` (models, forms, views, middleware, admin, migrations, tests).
- Templates live in top-level `templates/`; styles in `static/css/site.css`; browser behavior in `static/js/site.js`; geographic data in `static/data/`.
- Add automated tests for routes, forms, security, data integrity, and API behavior. A GitHub Actions workflow installs requirements and runs `python manage.py test` on pushes and pull requests to `main`.

## 3. Visual design and user experience

Create a polished civic/community organization website with a confident, trustworthy, welcoming tone. Follow the existing visual direction:

- Color variables are defined in CSS: deep navy/ink (`#0b2b50`), muted blue (`#4b6888`), primary blue (`#1058a8`), deep blue (`#0a3979`), pale sky blue (`#83d4ff`), accent blue/coral (`#2789d0`), green/blue accent (`#277bc0`), pale paper blue (`#eaf3ff`), near-white (`#f7faff`), and light blue border (`#c7dcf3`). These values are the source project's current palette even where variable names are unconventional.
- Use Aptos/Segoe UI sans-serif for body text and Georgia/Times New Roman serif for major headings.
- Maintain a centered content width near 1180px, clear section hierarchy, generous spacing, accessible contrast, responsive cards and forms, and a cohesive header/footer across public pages.
- Header becomes visually distinct after scrolling; responsive mobile navigation has an accessible toggle and closes after a navigation link is chosen.
- Provide responsive layouts around tablet/mobile widths, visible focus states, meaningful labels, appropriate autocomplete attributes, ARIA state for interactive controls, and respect `prefers-reduced-motion`.
- Use the supplied leadership photos and M4C logo from `static/images/`. Do not rely on unrelated stock political imagery.
- Avoid fake statistics, fabricated events, or unconfirmed local leaders. If source content labels a program/event/assignment as not yet confirmed, communicate that honestly.

## 4. Public pages and routes

Implement the following named routes and templates. Keep Django URL names stable where specified.

### `/` — home (`home`, `templates/index.html`)

- Hero section positioning M4C as a Kenyan peace movement, with the core message **“Promoting Peace, Unity & Constructive Dialogue Across Kenya.”** Use a strong visual identity and supplied M4C logo; the hero should not use the old generic `politician-1.jpeg`, `politician-2.jpeg`, or `politician-3.jpeg` assets as a substitute for the brand.
- About section: explain who M4C is and its vision/mission, including a peaceful Kenya and peace in action.
- Values section generated from server data: Peace, Unity, Integrity, Respect, Inclusivity, Dialogue, and Service, each with its short explanatory sentence and icon/accent.
- A statistics strip currently has the values `1000+ Peace Ambassadors`, `47 Counties Engaged`, `15K+ Citizens Mobilized`, and `500+ Community Leaders`. Treat these as supplied display content, not verified analytics; keep them editable in data rather than hardcoding in multiple places.
- “Get involved” / join section with tabs or toggles for **Join M4C** and **Member sign in**. Join form fields include full name, username, county, interest/role, email, WhatsApp phone number, password, and password confirmation. It posts to `/register/` with CSRF protection and shares the same member account flow as the dedicated registration page. The member sign-in panel posts to `/login/` and provides a link to account creation.
- Public volunteer registration is also supported through the JSON API at `POST /api/volunteers`; the browser JavaScript handles the volunteer form if present.
- Include quick links, social/community links, and contact details as represented in the supplied template. Existing public contact copy includes `movementforchange@gmail.com` and Nairobi, Kenya; don't invent contact channels or links.

### `/leadership/` — leadership (`leadership`, `templates/leadership.html`)

- Present national and regional leadership structures and county leadership structure, explaining responsibilities without implying unconfirmed positions are filled.
- Display the actual active national profiles supported by the current tests: National Chair (image supplied; the source profile's name is blank), Kimani W. Brian — National Secretary, Joseph Masini — National Coordinator, Rob Jilo — National Finance & Resource Mobilization, Jared Opiyo — National Operations, and Muchina Nyaga — National Media & Communication.
- The backend also contains a larger list of historic/region/county profile records, but current tests explicitly require that the page **not display** Brian Gitonga, Martin Kor, John Waithaka, Wanjeri Esther Stacy, Esther Muteri, or Moses Mwero in the active leadership listing. Respect the current page/tests rather than displaying every profile found in the Python constant.
- National Leadership, Regional Leadership, and County Leadership each list these 11 roles: Patron, Deputy Patron, Secretary, Mobilization / Organizing, Communications / Digital, Youth Groups Lead, Women Groups Lead, Finance / Resources, Research / Data, Discipline / Ethics, and Special Programmes / Stakeholder Relations. Do not label these as “11 members” if that misleadingly implies people are appointed; communicate them as roles/structure.

### `/comrades/` — campus participation (`comrades`, `templates/comrades.html`)

- Present “Comrades” as campus voices for peace and change.
- Campus roles: Campus Patron, Campus Chairperson, Deputy Chairperson, Secretary, Organizing Secretary, Treasurer, Communications / Digital Lead, Academic & Policy Lead, Welfare & Inclusion Lead, Mobilization Team, Class / Department Ambassadors.
- Sections cover campus activities, academic and policy engagement, welfare and inclusion, mobilization, class/department ambassadors, campus events, and a “Join Comrades” call to action.
- Where campus directories, institutions, representatives, dates, or locations are not yet confirmed, say they will be published once confirmed. Do not fabricate campus events.

### `/counties/` — county coverage (`counties`, `templates/counties.html`)

- Show M4C's Kenya-wide county network, searchable county list, interactive county map, and ward leadership context.
- Render an SVG map from the supplied geographic JSON/GeoJSON rather than relying on an external map API. County features come from `static/data/kenya-counties.geojson` (47 features). Ward features come from `static/data/kenya-wards.geojson` (1,450 features). Both contain boundaries and properties for navigation.
- County search form should locate/filter counties and allow users to select a county from the map or list. Selecting a county should display its county name, a summary, and subcounty/ward information. Include a way to return to the all-counties view.
- Keep geographic data attribution visible. The directory notes ward boundaries from geoBoundaries KEN ADM3 (CC BY 4.0; represented 2016), with county assignment derived from geoBoundaries KEN ADM2 and ADM1 containment. The map page/tests also require attribution references for **CC BY 4.0**, **CC BY 3.0 IGO**, and **Public Domain** as applicable to bundled datasets. Preserve accurate dataset attribution from each file's metadata.
- The directory `static/data/kenya-county-directory.json` has 47 counties, each with a slug and subcounty/ward names. Use this directory as the canonical source for ward lists; avoid maintaining duplicated hand-written lists.
- Include accessible names/keyboard behavior for SVG county paths, visible search results, loading/error handling for unavailable GeoJSON, and sensible mobile behavior.

### `/counties/<slug>/` — county detail (`county-detail`, `templates/county_detail.html`)

- Resolve the slug against the county profiles derived from the county directory. Show county name, local areas/subcounties, total ward count, ward listing grouped by subcounty, and leadership status.
- Current default data labels: `County Patron to be confirmed`, `Ward leadership structure under development`, and focus `Peacebuilding, outreach and mobilization`. Do not invent named patrons or ward officials.
- If a slug is unknown, return HTTP 404 and render a graceful “County profile not yet available” state.
- Confirmed data integrity: all 47 counties should be represented and the ward counts sum to 1,450. The Nairobi detail test expects Dagoretti and Mutu-ini Ward, plus the unconfirmed ward leadership label.

## 5. Member accounts and authentication

Use Django's built-in user model and authentication. Keep member profile fields separate in `MemberProfile`.

### Data models

1. `MemberProfile`
   - One-to-one relation to Django user, cascade on delete, related name `member_profile`.
   - `full_name` (max 150, blank/default empty), `phone_number` (max 16, unique), `county` (max 80, optional), and `interest` (max 80, optional).
2. `VolunteerRegistration`
   - `full_name` (max 150), `phone_number` (max 32), `county` (max 80), `interest` (max 80), optional blank email, `created_at` auto-added, ordered newest first. String representation includes name and county.

Keep the existing Django migrations or create equivalent clean migrations. Register appropriate models with Django admin so administrators can manage relevant records.

### `/register/` — account creation (`register`, `templates/register.html`)

- Redirect already-authenticated users to home.
- Form uses a custom `MemberCreationForm` derived from Django `UserCreationForm`; fields include full name, username, email, WhatsApp phone, county, role/interest, password and password confirmation.
- County options are the complete 47 counties. Role choices are Community Mobilizer, Youth Leader, Women Leader, Dialogue Facilitator, Faith Leader, General Volunteer, and Comrades / Campus Volunteer.
- Normalize phone numbers to international format: `00...` becomes `+...`, leading `0` becomes `+254...`, and leading `254` gets a plus. Validate as international E.164-like `+[1-9]` followed by 7–14 digits. Reject duplicate phone numbers and duplicate email addresses; normalize email to lowercase.
- Use Django password validation and accessible/autocomplete attributes. Save the Django user and MemberProfile atomically.
- After successful creation, atomically save the user and profile, sign the user in immediately, show a success message, and redirect to `/` (or the configured safe next destination). Do not send verification codes, require verified contact details, or redirect to a verification page.

### `/login/` — sign-in (`login`, `templates/login.html`)

- Support signing in with either username or registered email address. The custom `MemberAuthenticationForm` resolves an email identifier to its username before normal Django authentication.
- Authenticate normally with either username or registered email. Do not check email/phone verification status, send verification messages, or redirect to a verification page. On successful authentication, use Django `LoginView` behavior and redirect to the configured next/home destination.
- Otherwise use Django `LoginView` behavior and redirect to the configured next/home destination. Include CSRF protection and user-friendly invalid-credentials errors.

### `/logout/` — sign out

- Use Django `LogoutView`; provide a POST sign-out form with CSRF token on the profile page.

### `/profile/` — member profile (`profile`, `templates/profile.html`)

- Login required. Show full name (fallback to username), username/account details, phone, county, and interest, with a sign-out action. Do not display verification states or gate profile access based on contact details.

### Password reset routes

Use Django's built-in views with the supplied templates:
- `/password-reset/` (`password_reset`): collect account email and send reset email.
- `/password-reset/sent/` (`password_reset_done`): confirmation screen.
- `/password-reset/<uidb64>/<token>/` (`password_reset_confirm`): valid-link new-password form or expired/invalid-link state.
- `/password-reset/complete/` (`password_reset_complete`): completion screen.
- Use the text templates `password_reset_email.txt` and `password_reset_subject.txt`; use HTTPS links in email context for production.

## 6. Authentication and security

- Account creation and sign-in do not require email or phone verification. Do not implement contact-verification challenges, codes, links, resend flows, verification status fields, or verification-based access restrictions.
- Continue to use Django's password hashing and password validators. Keep registration and login CSRF-protected, validate and normalize submitted account fields as specified, and never log passwords or other credentials.
- Password-reset email uses Django's built-in flow and the configured SMTP settings. Read `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL` from the environment. The default sender is `Movement for Change <noreply@movementforchange.co.ke>`. Production requires a properly authorized sender/domain with SPF and DKIM configured; local development may use Django's console email backend. Avoid user enumeration in password-reset responses.

## 7. Volunteer JSON API

Endpoint: **`POST /api/volunteers`**, URL name `volunteer-registration`, only accepts POST.

- Request body is JSON object. Accept both camelCase legacy keys and snake_case keys:
  - `fullName` or `full_name`
  - `phoneNumber` or `phone_number`
  - `county`
  - `interest`
  - optional `email`
- Trim string values. Required: full name, phone number, county, interest. Validate lengths (name <=150, phone <=32, county <=80, interest <=80), and validate optional email with Django's email validator.
- On success persist a `VolunteerRegistration` and return HTTP 201 JSON with a thank-you message and registration ID. Do not return submitted private data unnecessarily.
- Error handling: malformed JSON returns 400 with `Invalid JSON`; non-object JSON returns 400 with `Invalid request body`; missing required fields returns 400 with a clear validation message; excessive lengths and invalid email return 400 with a clear message.
- Browser submissions include Django CSRF token and `X-CSRFToken`. A CSRF failure for this API returns HTTP 403 JSON message: `Your form security token expired. Reload the page and try again.`
- In `static/js/site.js`, handle pending, success, and error states; disable the submit button while pending; reset the form after success; if the server explicitly indicates a stale CSRF token, refresh the page and retry once with a new token; safely handle unexpected non-JSON responses and network errors.

## 8. Frontend JavaScript behavior

Use vanilla JS in `static/js/site.js` and guard page-specific logic so one shared script works on all pages:

- Header scroll state toggles `is-scrolled` after 20px.
- Accessible mobile menu toggles `aria-expanded`, label, and `is-open` class; close on navigation.
- Involvement tabs toggle `aria-pressed` and show/hide their associated panels.
- Volunteer API form submits JSON with CSRF and presents accessible status text.
- County map loads both GeoJSON files, renders SVG paths for counties and wards, computes a viewBox/projection from the loaded geometry, makes county paths selectable/clickable and keyboard-operable, supports county selection and back-to-all-counties behavior, and displays wards grouped by subcounty.
- Fail gracefully if a map dataset cannot load. Avoid unsafe HTML injection; create nodes and assign text safely.

## 9. Static assets and data

Use and preserve the bundled assets where relevant:

- `static/css/site.css`: full responsive stylesheet, typography, header/navigation, hero, content sections, cards, forms, maps, footer, breakpoints around 900px and 680px, reduced-motion behavior.
- `static/js/site.js`: interactions described above.
- `static/images/`: M4C logo and actual leadership portraits, with descriptive filenames and meaningful alt text.
- `static/data/kenya-county-directory.json`: authoritative 47-county hierarchy with subcounties and ward names, plus attribution metadata.
- `static/data/kenya-counties.geojson`: 47 county polygons, with `properties.name` and `properties.slug`.
- `static/data/kenya-wards.geojson`: 1,450 ward polygons, including `properties.wardName`, `properties.subcountyName`, `properties.countyName`, and `properties.countySlug`.
- Avoid duplicate/conflicting portrait files and avoid using image filenames with ambiguous/old labels in the active public leadership list.

## 10. Django settings and deployment

- Use `BASE_DIR`, top-level template directory, app templates, standard Django auth/session/messages/static apps, and middleware including SecurityMiddleware, WhiteNoise, sessions, common, CSRF, authentication, messages, and clickjacking protection. Do not add verification middleware.
- `ROOT_URLCONF = "m4c.urls"`; `WSGI_APPLICATION = "m4c.wsgi.application"`; login URL `/login/`; login and logout redirect to `/`.
- Default `LANGUAGE_CODE` is `en-us`, `TIME_ZONE` is `Africa/Nairobi`, `USE_I18N=True`, `USE_TZ=True`.
- Configure `STATIC_URL=/static/`, `STATIC_ROOT=BASE_DIR / "staticfiles"`, and `STATICFILES_DIRS=[BASE_DIR / "static"]`; use WhiteNoise for production static serving.
- Read `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, and `DATABASE_URL` from environment. Fail safely if production has no secret key; never rely on a development-only key in production. Keep `.env`, database, generated secret key, and credential files out of version control.
- Trusted HTTPS origins include the official M4C domains; when deployed behind Render or GitHub Codespaces forwarding, honor the forwarded HTTPS scheme and configure the matching trusted origin. Do not broadly disable CSRF.
- `start.sh` should ensure a secret key exists (prefer hosting environment; if generated locally, store it in a private ignored file), set production debug default to false, run `python manage.py migrate --noinput`, then exec `python run_tornado.py`.
- `Procfile` delegates to `sh start.sh`. `run_tornado.py` binds to `0.0.0.0` and defaults to port 8000, allowing `HOST` and `PORT` overrides.
- `docker-compose.base44.yml` provides a local Python 3.12 slim container, mounts the repository at `/app`, maps host port 3000 to container port 8000, installs requirements, migrates, and runs Django's dev server with auto-reload.
- `README.md` should document virtualenv setup, install, migrations, dev server, Tornado server, database environment, production SMTP setup for password reset, and deployment caveats.

## 11. Tests and acceptance criteria

Create and run Django tests. The finished application should satisfy these acceptance criteria:

1. `python manage.py test` passes.
2. Public routes `/`, `/leadership/`, `/comrades/`, `/counties/`, and `/counties/nairobi/` render successfully; unknown county slugs return 404.
3. Home page includes a CSRF-protected join flow, member sign-in panel, and join fields including full name, county, and interest.
4. Leadership page includes the active national leadership roles/names described above and excludes the six names specifically marked inactive for the current listing.
5. County directory has exactly 47 counties and the ward dataset exactly 1,450 features; all ward features have county, subcounty, and ward names; ward counts sum to 1,450.
6. Nairobi county detail contains Dagoretti and Mutu-ini Ward and identifies ward leadership as unconfirmed.
7. Comrades page includes Campus Patron, Academic & Policy Lead, Class / Department Ambassadors, Campus Events, and Join Comrades.
8. Volunteer API correctly handles valid payloads, camelCase/snake_case aliases, malformed JSON, non-object JSON, missing fields, invalid email, excessive lengths, CSRF failures, and successful persistence.
9. Authentication supports username/email sign-in, immediate account access after creation, profile access without verification gates, logout, and password reset. Signup and login do not send or require email/phone verification.
11. No real credentials, private tokens, production passwords, or secret key values are included in source code, prompts, logs, or generated documentation. Use placeholders such as `<SET_IN_DEPLOYMENT_ENVIRONMENT>`.
12. Website is responsive, keyboard accessible, uses CSRF protection, and does not invent leadership assignments, events, or geographic information.

## 12. Important source-of-truth and cleanup notes

- Some repository documentation is stale or contradictory. Follow the actual Python models, migrations, current templates, and tests, while honoring this prompt's requirement that member signup and login do not require contact verification.
- The active leadership template behavior and tests take precedence over unused/legacy entries in `LEADERSHIP_PROFILES`.
- The codebase is Django-template-based, not a Base44-only or React application. Preserve the existing architecture unless the user explicitly requests a migration.
- The zip contains many portrait files at the project root as well as copies under `static/images/`; use the canonical static paths in templates and avoid exposing unnecessary duplicate root-level files.
- Keep production secrets external. Document the names of required environment variables but never include their real values.

## Expected deliverable

Return a complete, working repository with all required source files, templates, static assets, geographic data, migrations, tests, and deployment documentation. Include a concise summary of the implemented features, setup/run instructions, environment variables needed for production, and the results of the test suite. If anything cannot be implemented exactly because source data is missing or contradictory, state the limitation explicitly instead of inventing details.
