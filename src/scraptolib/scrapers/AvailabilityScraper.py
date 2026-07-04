import datetime
import re

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from scraptolib.utils.helpers import human_delay
from scraptolib.scrapers.Scraper import Scraper

# French month names for parsing date headings
_FRENCH_MONTHS = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}


class AvailabilityScraper(Scraper):
    """
    Scraper designed to extract appointment availability slots from Doctolib booking pages.

    Inherits from `Scraper` and provides specialized methods to:
    - Navigate the booking flow (cookie banner, motive selection)
    - Expand each displayed day card
    - Click "Voir plus" to reveal all hidden slots for each day
    - Extract the date label and every time slot for all displayed days
    - Annotate each slot with the name of the person handling the consultation

    Methods
    -------
    __init__()
        Initializes the AvailabilityScraper. ChromeDriver is resolved automatically
        via Selenium Manager.

    select_motive(motive_text: str | None) -> bool
        Clicks the motive button matching `motive_text` on the motive selection step.
        If None, picks the first available motive.
        Returns True if found and clicked, False otherwise.

    is_on_motive_page() -> bool
        Returns True if the current page is the motive selection step.

    is_on_availabilities_page() -> bool
        Returns True if the current page is the availabilities step (heading present).

    get_practitioner_name() -> str
        Returns the practitioner name from the booking sidebar.

    get_day_cards() -> list[WebElement]
        Returns all day card elements currently displayed on the page.

    expand_day(card: WebElement)
        If a day card is collapsed, clicks its expand button.

    click_voir_plus_in_card(card: WebElement)
        Clicks the "Voir plus" button inside a day card to reveal all hidden slots.

    get_day_date(card: WebElement) -> str
        Returns the date heading text of a given day card.

    get_substitution_legends_in_card(card: WebElement) -> dict[str, str]
        Returns a mapping of legend IDs to substitute names for a given day card.

    get_day_slots(card: WebElement, practitioner_name: str, date_obj: date | None) -> list[dict]
        Returns a list of dicts for each time slot in the given day card with keys:
            - datetime: str (e.g. "2026-06-18 08:00")
            - handled_by: str (practitioner name or substitute name)

    run_scraping(availability_url: str, motive_text: str | None = None, weeks: int = 4) -> dict
        Full scraping workflow. Navigates to the page, handles the booking flow,
        loads dates for the specified number of weeks, then extracts slots for
        every displayed day.

        Parameters
        ----------
        availability_url : str
            Full URL to the practitioner's booking/availabilities page.
        motive_text : str | None, optional
            Text of the motive button to click. If None and a motive step is shown,
            the first available motive is selected automatically.

        Returns
        -------
        dict
            {
                "practitioner": str,
                "days": list[dict],
                    # Each day dict:
                    # {
                    #     "date": str,  # "YYYY-MM-DD"
                    #     "slots": list[dict],  # [{"datetime": "YYYY-MM-DD HH:MM", "handled_by": "..."}, ...]
                    # }
                "scrap_timestamp": str   # YYYY-MM-DD HH:MM:SS
            }

            "practitioner" is the person who owns the Doctolib profile.
            "handled_by" in each slot indicates who actually ensures the consultation
            (same as practitioner when no substitution badge, or the collaborator name
            when a blue dot is present).
    """

    def __init__(self):
        super().__init__()

    # ------------------------------------------------------------------
    # Motive selection
    # ------------------------------------------------------------------

    def select_motive(self, motive_text: str | None = None) -> bool:
        """
        Click a motive button on the motive selection step.
        If `motive_text` is None, clicks the first motive available.
        Returns True if a motive was clicked, False otherwise.
        """
        try:
            if motive_text:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//button[.//p[contains(text(), '{motive_text}')]]")
                    )
                )
            else:
                btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//ul//li//button[.//p]")
                    )
                )
            btn.click()
            human_delay()
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Page detection
    # ------------------------------------------------------------------

    def is_on_profile_page(self) -> bool:
        """Check if we are on the practitioner's profile page (not the booking flow)."""
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[contains(., 'Prendre rendez-vous')]")
                )
            )
            return True
        except TimeoutException:
            return False

    def click_prendre_rendez_vous(self):
        """
        Click the 'Prendre rendez-vous' link on the practitioner's profile page
        to enter the booking flow.
        """
        link = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(., 'Prendre rendez-vous')]")
            )
        )
        link.click()
        human_delay()

    def is_on_motive_page(self) -> bool:
        """Check if we are on the motive selection step."""
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h1[contains(text(), 'motif de consultation')]")
                )
            )
            return True
        except TimeoutException:
            return False

    def is_on_availabilities_page(self) -> bool:
        """Check if we landed on the availabilities step."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h1[contains(text(), 'date de consultation')]")
                )
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Day cards
    # ------------------------------------------------------------------

    def _parse_french_date(self, date_text: str) -> datetime.date | None:
        """
        Parse a French date heading like 'Jeudi 18 juin 2026' into a datetime.date.
        Returns None if parsing fails.
        """
        # Expected format: "DayName DD month YYYY"
        match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", date_text)
        if not match:
            return None
        day = int(match.group(1))
        month_name = match.group(2).lower()
        year = int(match.group(3))
        month = _FRENCH_MONTHS.get(month_name)
        if not month:
            return None
        try:
            return datetime.date(year, month, day)
        except ValueError:
            return None

    def _get_date_span_days(self) -> int:
        """
        Return the number of calendar days between the first and last displayed day card.
        Returns 0 if dates cannot be determined.
        """
        cards = self.driver.find_elements(
            By.CSS_SELECTOR, "div.dl-card.dl-card-variant-stroke"
        )
        if len(cards) < 2:
            return 0

        first_heading = cards[0].find_element(By.TAG_NAME, "h2")
        last_heading = cards[-1].find_element(By.TAG_NAME, "h2")

        first_text = first_heading.get_attribute("textContent").strip()
        last_text = last_heading.get_attribute("textContent").strip()

        first_date = self._parse_french_date(first_text)
        last_date = self._parse_french_date(last_text)

        if first_date and last_date:
            return (last_date - first_date).days
        return 0

    def load_more_dates(self, weeks: int = 4):
        """
        Click the 'Voir plus de dates' button repeatedly until the displayed date range
        covers at least `weeks` weeks (default 4), or the button disappears.

        Uses full mouse event dispatch (mousedown/mouseup/click) because the React
        Tappable component doesn't respond to a simple JS .click().
        """
        target_days = weeks * 7

        while True:
            span = self._get_date_span_days()
            if span >= target_days:
                self.lg.info(
                    f"Date span is {span} days (>= {target_days}), done loading."
                )
                break

            try:
                voir_plus_dates_btn = self.driver.find_element(
                    By.XPATH, "//button[.//span[contains(text(), 'Voir plus de dates')] or contains(., 'Voir plus de dates')]"
                )
            except NoSuchElementException:
                self.lg.info("'Voir plus de dates' button not found, all dates loaded.")
                break

            self.driver.execute_script("""
                var btn = arguments[0];
                btn.scrollIntoView({block: 'center'});
                btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true}));
                btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, cancelable: true}));
                btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            """, voir_plus_dates_btn)
            human_delay(low=1, high=2)

    def get_day_cards(self):
        """Return all day card elements currently displayed on the page."""
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.dl-card.dl-card-variant-stroke")
            )
        )
        return self.driver.find_elements(
            By.CSS_SELECTOR, "div.dl-card.dl-card-variant-stroke"
        )

    def expand_day(self, card):
        """
        If a day card is collapsed, click its expand button ('Afficher ...').
        Does nothing if the card is already expanded.
        Uses JavaScript click to avoid interception by overlapping elements.
        """
        try:
            expand_btn = card.find_element(
                By.XPATH, ".//button[contains(@aria-label, 'Afficher')]"
            )
            self.driver.execute_script("arguments[0].click();", expand_btn)
            human_delay(low=1, high=2)
        except NoSuchElementException:
            pass  # already expanded

    def click_voir_plus_in_card(self, card):
        """
        Click the 'Voir plus' button within a day card to reveal all hidden slots.
        Uses full mouse event dispatch (mousedown/mouseup/click) because the React
        Tappable component doesn't respond to a simple JS .click().
        Does nothing if the button is absent.
        """
        try:
            voir_plus_btn = card.find_element(
                By.CSS_SELECTOR, "[data-test='more'] button"
            )
            self.driver.execute_script("""
                var btn = arguments[0];
                btn.scrollIntoView({block: 'center'});
                btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true}));
                btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, cancelable: true}));
                btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            """, voir_plus_btn)
            human_delay(low=1, high=2)
        except NoSuchElementException:
            pass  # no hidden slots

    # ------------------------------------------------------------------
    # Data extraction
    # ------------------------------------------------------------------

    def get_practitioner_name(self) -> str:
        """
        Return the practitioner name from the booking detail sidebar.
        This is the person who owns the page.
        """
        try:
            aside = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "aside"))
            )
            name_elem = aside.find_element(By.TAG_NAME, "p")
            return name_elem.get_attribute("textContent").strip()
        except (TimeoutException, NoSuchElementException):
            return ""

    def get_day_date(self, card) -> str:
        """Return the date heading text of the given day card."""
        try:
            heading = card.find_element(By.TAG_NAME, "h2")
            return heading.get_attribute("textContent").strip()
        except NoSuchElementException:
            return ""

    def get_substitution_legends_in_card(self, card) -> dict[str, str]:
        """
        Parse legend elements within a day card to build a map of
        legend ID -> substitute name.

        The legend text follows the pattern:
            "Indique une consultation assurée par un collaborateur : <Name>"
        We extract the name after ": ".
        """
        legends = card.find_elements(By.CSS_SELECTOR, ".dl-availabilities-legend")

        legend_map = {}
        for legend in legends:
            legend_id = legend.get_attribute("id")
            text = legend.get_attribute("textContent").strip()
            if ": " in text:
                substitute_name = text.split(": ", 1)[-1]
            else:
                substitute_name = text
            if legend_id:
                legend_map[legend_id] = substitute_name

        return legend_map

    def get_day_slots(self, card, practitioner_name: str, date_obj: datetime.date | None = None) -> list[dict]:
        """
        Return all time slots for a given day card, each annotated with
        who handles the consultation and a full datetime.

        Parameters
        ----------
        card : WebElement
            The day card element to extract slots from.
        practitioner_name : str
            The name of the page owner, used as default when no substitution badge is present.
        date_obj : datetime.date | None
            The parsed date for this day card, used to build full datetime strings.

        Returns
        -------
        list[dict]
            Each dict has keys: "datetime", "handled_by".
        """
        legend_map = self.get_substitution_legends_in_card(card)
        slot_items = card.find_elements(By.CSS_SELECTOR, ".availabilities-slot-button")

        slots = []
        for item in slot_items:
            btn = item.find_element(By.TAG_NAME, "button")
            time_text = btn.get_attribute("textContent").strip()
            if not time_text:
                continue

            # Build full datetime string
            if date_obj and re.match(r"^\d{2}:\d{2}$", time_text):
                dt_str = f"{date_obj.strftime('%Y-%m-%d')} {time_text}"
            else:
                dt_str = time_text

            # Check if this slot has a substitution badge
            badges = item.find_elements(By.CSS_SELECTOR, "[data-test-id*='substitution-badge']")
            if badges:
                described_by = btn.get_attribute("aria-describedby") or ""
                handled_by = legend_map.get(described_by, "Collaborateur")
            else:
                handled_by = practitioner_name

            slots.append({
                "datetime": dt_str,
                "handled_by": handled_by,
            })

        return slots

    # ------------------------------------------------------------------
    # Main workflow
    # ------------------------------------------------------------------

    def run_scraping(self, availability_url: str, motive_text: str | None = None, weeks: int = 4) -> dict:
        """
        Navigate to the booking page, handle the flow, and extract availability slots
        for all days over the specified number of weeks.

        Parameters
        ----------
        availability_url : str
            Full Doctolib booking URL (booking/availabilities or booking root).
        motive_text : str | None
            Motive button text to select. None = pick the first one automatically.
        weeks : int
            Number of weeks of availability to load (default 4).

        Returns
        -------
        dict with keys: practitioner, days, scrap_timestamp
        """
        self.start_driver()
        self.driver.get(availability_url)
        human_delay()

        # Handle retry-later / error page
        if self.is_retry_later():
            self.handle_retry_later(current_page=availability_url)

        # Handle cookies
        self.handle_cookies()

        # If we are on the practitioner's profile page, click "Prendre rendez-vous"
        if self.is_on_profile_page():
            self.lg.info("On profile page, clicking 'Prendre rendez-vous'...")
            self.click_prendre_rendez_vous()

        # If we land on the motive selection step, pick one
        if self.is_on_motive_page():
            self.lg.info("Motive selection step detected, selecting motive...")
            selected = self.select_motive(motive_text)
            if not selected:
                self.lg.warning("Could not select a motive, aborting.")
                self.stop_driver()
                return {}

        # Wait for the availabilities page
        if not self.is_on_availabilities_page():
            self.lg.warning("Did not reach the availabilities page.")
            self.stop_driver()
            return {}

        self.lg.info("On availabilities page, extracting slots...")

        # Get practitioner name from sidebar
        practitioner_name = self.get_practitioner_name()
        self.lg.info(f"Practitioner: {practitioner_name}")

        # Shrink the page so all day cards are visible and clickable
        self.driver.execute_script("document.body.style.zoom='1%'")

        # Load more dates until we cover the requested number of weeks
        self.load_more_dates(weeks=weeks)

        # Iterate over all displayed day cards
        day_cards = self.get_day_cards()
        self.lg.info(f"{len(day_cards)} day(s) displayed")

        days = []

        for card in day_cards:
            self.expand_day(card)
            self.click_voir_plus_in_card(card)

            date_text = self.get_day_date(card)
            date_obj = self._parse_french_date(date_text)
            date_str = date_obj.strftime("%Y-%m-%d") if date_obj else date_text

            slots = self.get_day_slots(card, practitioner_name, date_obj)

            days.append({
                "date": date_str,
                "slots": slots,
            })

            self.lg.info(f"  {date_str} — {len(slots)} slot(s)")
            for slot in slots:
                self.lg.info(f"    {slot['datetime']} — {slot['handled_by']}")

        self.stop_driver()

        return {
            "practitioner": practitioner_name,
            "days": days,
            "scrap_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


if __name__ == "__main__":
    print("test")
