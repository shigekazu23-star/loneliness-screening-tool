# ---- System (end-to-end) and acceptance tests ----
# These drive a real browser against the production frontend build talking to
# the Flask API and SQLite, so they exercise the whole stack the way a user
# does. Following the testing pyramid, they sit above the unit tests (15) and
# integration tests (9) already in tests/, and they mix functional checks with
# acceptance checks: every scenario states the requirement it accepts, using
# the module identifiers (M1-M7) fixed in the Unit 3 design.
#
# Scenarios are written in given-when-then form so that a non-technical reader
# can confirm the system meets the intent, not just the code.
#
# Run:  python -m pytest tests/e2e -v
# Prerequisite: cd src/frontend && npm run build

import pytest
from playwright.sync_api import expect

DEMO_PASSWORD = "Passw0rd!demo"

# Traceability: scenario -> requirement accepted (Unit 3 module design)
REQUIREMENTS = {
    "login": "M1 authentication",
    "consent": "M2 versioned, revocable consent",
    "questionnaire": "M3 input validation + M4 scoring",
    "dashboard": "M6 trend and risk flag + M7 visualisation",
    "caregiver": "M1 role-based access + M2 consent gate",
}


def login(page, username, password=DEMO_PASSWORD):
    """Given a registered user, when they log in, then the app opens."""
    page.fill("#username", username)
    page.fill("#password", password)
    page.get_by_role("button", name="Log in", exact=True).click()


# ---------------------------------------------------------------- happy path


@pytest.mark.acceptance
def test_older_adult_completes_a_screening_cycle(app_page):
    """M3+M4+M7: answering the three items produces a score and a record.

    Given an older adult with an active consent,
    when they answer the three loneliness items and submit,
    then a score between 3 and 9 is stored and shown on the dashboard.
    """
    page = app_page
    login(page, "tanaka")

    page.get_by_role("button", name="Answer again").click()
    expect(page.get_by_text("Today's three questions")).to_be_visible()

    # Answer every item with the middle option ("Some of the time" = 2).
    for group in page.locator(".choice-group").all():
        group.locator("label.choice").nth(1).click()
    page.get_by_role("button", name="Send my answers").click()

    expect(page.get_by_text("Score this time")).to_be_visible()
    score = int(page.locator(".score-big").inner_text())
    assert 3 <= score <= 9, f"score {score} outside the valid range"


@pytest.mark.acceptance
def test_worsening_trajectory_raises_the_flag_in_the_interface(app_page):
    """M6: a sustained or worsening pattern surfaces a warning to the user.

    Given the seeded account whose scores worsen over time,
    when the dashboard is displayed,
    then the risk flag is shown as a warning, not as a neutral message.
    """
    page = app_page
    login(page, "sato")

    expect(page.get_by_text("Your records")).to_be_visible()
    expect(page.locator(".status-warn")).to_be_visible()
    expect(page.locator(".status-warn")).to_contain_text("talk")


@pytest.mark.acceptance
def test_stable_trajectory_does_not_raise_the_flag(app_page):
    """M6: a stable low pattern must stay silent (no false alarm).

    Given the seeded account whose scores stay low and stable,
    when the dashboard is displayed,
    then the neutral status is shown and no warning appears.
    """
    page = app_page
    login(page, "tanaka")

    expect(page.locator(".status-ok")).to_be_visible()
    expect(page.locator(".status-warn")).to_have_count(0)


@pytest.mark.acceptance
def test_caregiver_sees_only_consented_people(app_page):
    """M1+M2: role-based access plus the consent gate govern the overview.

    Given a caregiver linked to three consenting older adults,
    when the caregiver opens the supporter page,
    then all three appear with their latest score and attention state.
    """
    page = app_page
    login(page, "kaigo")

    expect(page.get_by_text("Supporter page")).to_be_visible()
    cards = page.locator(".person-card")
    expect(cards).to_have_count(3)
    expect(page.get_by_text("Taro Sato")).to_be_visible()


@pytest.mark.acceptance
def test_language_toggle_switches_the_whole_interface(app_page):
    """Japanese-first design (Unit 1): the interface must switch languages.

    Given the evaluation build running in English,
    when the language toggle is pressed,
    then the interface strings change to Japanese.
    """
    page = app_page
    expect(page.get_by_text("Loneliness Check")).to_be_visible()

    page.get_by_role("button", name="日本語").click()
    expect(page.get_by_text("こころの健康チェック")).to_be_visible()


# -------------------------------------------------------------- unhappy path


@pytest.mark.acceptance
def test_wrong_password_is_rejected_with_a_clear_message(app_page):
    """M1: authentication failures must be explicit and must not sign in.

    Given a registered user,
    when the password is wrong,
    then an error message appears and no session starts.
    """
    page = app_page
    login(page, "tanaka", password="not-the-password")

    expect(page.locator(".error")).to_be_visible()
    expect(page.get_by_text("Your records")).to_have_count(0)


@pytest.mark.acceptance
def test_incomplete_answers_are_refused(app_page):
    """M3: submitting fewer than three answers must be blocked client-side.

    Given the questionnaire,
    when only one item is answered and the form is submitted,
    then a validation message appears and no score is produced.
    """
    page = app_page
    login(page, "tanaka")
    page.get_by_role("button", name="Answer again").click()

    page.locator(".choice-group").first.locator("label.choice").first.click()
    page.get_by_role("button", name="Send my answers").click()

    expect(page.locator(".error")).to_be_visible()
    expect(page.get_by_text("Score this time")).to_have_count(0)


@pytest.mark.acceptance
def test_withdrawing_consent_removes_the_person_from_the_caregiver_view(
    app_page, frontend
):
    """M2: withdrawal takes effect on the caregiver's next read, not later.

    Given an older adult visible to their caregiver,
    when that person withdraws consent,
    then the caregiver no longer sees them on the supporter page.
    """
    page = app_page

    login(page, "suzuki")
    page.get_by_role("button", name="Withdraw consent").click()
    expect(page.locator(".status-ok")).to_contain_text("withdrawn")

    page.evaluate("() => sessionStorage.clear()")
    page.goto(frontend)
    login(page, "kaigo")

    expect(page.get_by_text("Supporter page")).to_be_visible()
    expect(page.locator(".person-card")).to_have_count(2)
    expect(page.get_by_text("Yoshiko Suzuki")).to_have_count(0)
