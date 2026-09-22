"""
Módulo de scraping de Google Maps.
Basado en un scraper open-source, corregido para:
- No depender de una ruta fija de Chrome en Windows (deja que Playwright use su propio navegador).
- No borrar columnas de datos válidos.
- Correr en modo headless (sin ventana visible), ideal para dejarlo corriendo en segundo plano.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass, asdict

from playwright.sync_api import sync_playwright, Page


@dataclass
class Place:
    name: str = ""
    address: str = ""
    website: str = ""
    phone_number: str = ""
    reviews_count: Optional[int] = None
    reviews_average: Optional[float] = None
    store_shopping: str = "No"
    in_store_pickup: str = "No"
    store_delivery: str = "No"
    place_type: str = ""
    opens_at: str = ""
    introduction: str = ""


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def extract_text(page: Page, xpath: str) -> str:
    try:
        if page.locator(xpath).count() > 0:
            return page.locator(xpath).first.inner_text()
    except Exception as e:
        logging.warning(f"No se pudo extraer texto para {xpath}: {e}")
    return ""


def extract_place(page: Page) -> Place:
    name_xpath = '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]'
    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
    reviews_count_xpath = '//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span//span//span[@aria-label]'
    reviews_average_xpath = '//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span[@aria-hidden]'
    info1 = '//div[@class="LTs0Rc"][1]'
    info2 = '//div[@class="LTs0Rc"][2]'
    info3 = '//div[@class="LTs0Rc"][3]'
    opens_at_xpath = '//button[contains(@data-item-id, "oh")]//div[contains(@class, "fontBodyMedium")]'
    opens_at_xpath2 = '//div[@class="MkV9"]//span[@class="ZDu9vd"]//span[2]'
    place_type_xpath = '//div[@class="LBgpqf"]//button[@class="DkEaL "]'
    intro_xpath = '//div[@class="WeS02d fontBodyMedium"]//div[@class="PYvSYb "]'

    place = Place()
    place.name = extract_text(page, name_xpath)
    place.address = extract_text(page, address_xpath)
    place.website = extract_text(page, website_xpath)
    place.phone_number = extract_text(page, phone_number_xpath)
    place.place_type = extract_text(page, place_type_xpath)
    place.introduction = extract_text(page, intro_xpath) or "No encontrada"

    reviews_count_raw = extract_text(page, reviews_count_xpath)
    if reviews_count_raw:
        try:
            temp = reviews_count_raw.replace("\xa0", "").replace("(", "").replace(")", "").replace(",", "")
            place.reviews_count = int(temp)
        except Exception as e:
            logging.warning(f"No se pudo convertir el número de reseñas: {e}")

    reviews_avg_raw = extract_text(page, reviews_average_xpath)
    if reviews_avg_raw:
        try:
            temp = reviews_avg_raw.replace(" ", "").replace(",", ".")
            place.reviews_average = float(temp)
        except Exception as e:
            logging.warning(f"No se pudo convertir el promedio de reseñas: {e}")

    for info_xpath in (info1, info2, info3):
        info_raw = extract_text(page, info_xpath)
        if info_raw:
            temp = info_raw.split("·")
            if len(temp) > 1:
                check = temp[1].replace("\n", "").lower()
                if "shop" in check or "compra" in check:
                    place.store_shopping = "Yes"
                if "pickup" in check or "retiro" in check:
                    place.in_store_pickup = "Yes"
                if "delivery" in check or "entrega" in check or "domicilio" in check:
                    place.store_delivery = "Yes"

    opens_at_raw = extract_text(page, opens_at_xpath)
    if opens_at_raw:
        opens = opens_at_raw.split("⋅")
        place.opens_at = (opens[1] if len(opens) > 1 else opens_at_raw).replace("\u202f", "")
    else:
        opens_at2_raw = extract_text(page, opens_at_xpath2)
        if opens_at2_raw:
            opens = opens_at2_raw.split("⋅")
            place.opens_at = (opens[1] if len(opens) > 1 else opens_at2_raw).replace("\u202f", "")

    return place


def scrape_places(search_for: str, total: int, progress_callback=None) -> List[Place]:
    """
    Busca `search_for` en Google Maps y devuelve hasta `total` resultados.
    progress_callback(mensaje: str) es opcional, para mostrar avance en una interfaz.
    """
    setup_logging()
    places: List[Place] = []

    def notify(msg: str):
        logging.info(msg)
        if progress_callback:
            progress_callback(msg)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        page = browser.new_page()
        try:
            page.goto("https://www.google.com/maps?hl=es", timeout=60000)
            page.wait_for_timeout(1000)
            page.locator("//form[contains(@jsaction,'searchboxFormSubmit')]//input[@name='q']").fill(search_for)
            page.keyboard.press("Enter")
            page.wait_for_selector('//a[contains(@href, "https://www.google.com/maps/place")]', timeout=30000)
            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            max_scrolls = 40
            scrolls = 0
            while scrolls < max_scrolls:
                page.mouse.wheel(0, 10000)
                page.wait_for_timeout(1500)
                found = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                notify(f"Negocios encontrados hasta ahora: {found}")
                if found >= total:
                    break
                if found == previously_counted:
                    notify("Se llegó al final de los resultados disponibles.")
                    break
                previously_counted = found
                scrolls += 1

            listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
            listings = [listing.locator("xpath=..") for listing in listings]
            notify(f"Se van a revisar {len(listings)} negocios en detalle...")

            for idx, listing in enumerate(listings):
                try:
                    listing.click()
                    page.wait_for_selector(
                        '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]', timeout=10000
                    )
                    page.wait_for_timeout(1200)
                    place = extract_place(page)
                    if place.name:
                        places.append(place)
                        notify(f"[{idx + 1}/{len(listings)}] {place.name}")
                    else:
                        notify(f"[{idx + 1}/{len(listings)}] Sin nombre, se omite.")
                except Exception as e:
                    notify(f"[{idx + 1}/{len(listings)}] Error al extraer: {e}")
        finally:
            browser.close()
    return places
