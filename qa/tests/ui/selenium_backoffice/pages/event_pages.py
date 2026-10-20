from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .base_page import BasePage


class EventFormPage(BasePage):
    path = "/admin/events/new"

    SUBMIT = (By.CSS_SELECTOR, "form button.btn-primary")

    def fill(self, title, city, starts_at, capacity, venue="", status="published"):
        self.type(self.field("Titre"), title)
        self.type(self.field("Ville"), city)
        self.type(self.field("Lieu"), venue)
        self.set_value_js(self.field("Date et heure"), starts_at)  # format YYYY-MM-DDTHH:MM
        self.type(self.field("Capacite"), str(capacity))
        Select(self.find(self.field("Statut", "select"))).select_by_value(status)
        return self

    def submit(self):
        self.click(self.SUBMIT)
        self.wait.until(lambda d: d.current_url.rstrip("/").split("/")[-1].isdigit())
        return EventManagePage(self.driver, self.base_url)


class EventManagePage(BasePage):
    TITLE = (By.CSS_SELECTOR, "h1.page-title")
    CATEGORY_ROWS = (By.XPATH, "//h3[text()='Categories de billets']/following-sibling::div[1]//tbody/tr")
    NEW_CAT_NAME = (By.CSS_SELECTOR, "input[placeholder='Nom']")
    ADD_CAT = (By.XPATH, "//button[contains(., 'Ajouter')]")

    def title(self):
        return self.text_of(self.TITLE)

    def add_category(self, name, price_eur, quota):
        self.type(self.NEW_CAT_NAME, name)
        self.type(self.field("Prix (EUR)"), str(price_eur))
        self.type(self.field("Quota"), str(quota))
        self.click(self.ADD_CAT)
        self.wait.until(lambda d: name in self.category_names())

    def category_names(self):
        return self.texts(self.CATEGORY_ROWS, "td")
