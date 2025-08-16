from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus
import re


def clean_price(price_str):
    """Convert a price string like '₦ 250,000' into an integer 250000."""
    match = re.search(r'[\d,]+', price_str.replace("\xa0", " "))
    if match:
        return int(match.group(0).replace(",", ""))
    return float('inf')  # If no valid price, push to end when sorting


def scrape_jumia(search_item):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # change to True if you don't want to see the browser
        page = browser.new_page()

        # Go to the Jumia search page
        page.goto(f"https://www.jumia.com.ng/catalog/?q={search_item}")

        # Wait for products to load
        page.wait_for_selector("article.prd")

        # Select all product elements
        products = page.query_selector_all("article.prd")

        results = []
        for product in products:
            # Extract title
            title = product.query_selector("h3.name").inner_text() if product.query_selector("h3.name") else "No title"

            # Extract price
            price = product.query_selector("div.prc").inner_text() if product.query_selector("div.prc") else "No price"
            price_val = clean_price(price)

            # Extract link
            link = product.query_selector("a.core").get_attribute("href") if product.query_selector("a.core") else None
            full_link = f"https://www.jumia.com.ng{link}" if link else "No link"

            # Extract image
            img = product.query_selector("img")
            image_url = img.get_attribute("data-src") if img and img.get_attribute("data-src") else (
                img.get_attribute("src") if img else "Image not found"
            )

            results.append({
                "title": title,
                "price": price_val,
                "link": full_link,
                "image": image_url
            })

        browser.close()
        return results

def scrape_jiji(search_term, page_number=1):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = (
            f"https://jiji.ng/search?query={search_term.replace(' ', '+')}"
            f"&page={page_number}"
        )
        page.goto(url)
        # Wait for product card selector based on Java version
        page.wait_for_selector("div.b-list-advert__gallery__item.js-advert-list-item", timeout=10000)

        product_cards = page.query_selector_all("div.b-list-advert__gallery__item.js-advert-list-item")
        results = []

        for card in product_cards:
            link_tag = card.query_selector("a[href]")
            full_link = f"https://jiji.ng{link_tag.get_attribute('href')}" if link_tag else "No link"

            title_tag = card.query_selector(".b-advert-title-inner.qa-advert-title")
            title = title_tag.inner_text().strip() if title_tag else "No title"

            price_tag = card.query_selector(".qa-advert-price")
            price = price_tag.inner_text().strip() if price_tag else "No price"

            desc_tag = card.query_selector(".b-list-advert-base__description-text")
            description = desc_tag.inner_text().strip() if desc_tag else "No description"

            img_tag = card.query_selector("picture img")
            image_url = img_tag.get_attribute("src") if img_tag else "Image not found"

            results.append({
                "title": title,
                "price": price,
                "description": description,
                "link": full_link,
                "image": image_url
            })

        browser.close()
        return results

def scrape_konga(search_item, page_number=1):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Change to True for headless mode
        page = browser.new_page()

        # Build Konga search URL
        search_url = f"https://www.konga.com/search?search={quote_plus(search_item)}&page={page_number}"
        page.goto(search_url)

        # Wait for product list to load
        page.goto(search_url, timeout=60000, wait_until="domcontentloaded")

        # Select all product elements
        products = page.query_selector_all("li.List_listItem__KlvU2")
        results = []

        for product in products:
            # Extract title
            title_tag = product.query_selector("h3.ListingCard_productTitle__9Kzxv")
            title = title_tag.inner_text().strip() if title_tag else "No title"

            # Extract price
            price_tag = product.query_selector("span.shared_initialPrice__cTRSe")
            price = price_tag.inner_text().strip() if price_tag else "No price"

            # Extract link
            link_tag = product.query_selector("a")
            link = link_tag.get_attribute("href") if link_tag else None
            full_link = f"https://www.konga.com{link}" if link else "No link"

            # Extract image
            img_tag = product.query_selector("img")
            image_url = img_tag.get_attribute("src") if img_tag else "Image not found"

            results.append({
                "title": title,
                "price": price,
                "link": full_link,
                "image": image_url
            })

        browser.close()
        return 0
    return None


def scrape_all_sorted(search_item):
    """Run all scrapers, merge results, and sort by price_value."""
    all_results = []

    try:
        all_results.extend(scrape_jumia(search_item))
    except Exception as e:
        print(f"⚠️ Jumia scraper failed: {e}")

    try:
        all_results.extend(scrape_jiji(search_item))
    except Exception as e:
        print(f"⚠️ Jiji scraper failed: {e}")

    try:
        all_results.extend(scrape_konga(search_item))
    except Exception as e:
        print(f"⚠️ Konga scraper failed: {e}")

    # Sort safely: skip results without a valid price
    all_results = [item for item in all_results if isinstance(item.get("price"), (int, float))]
    all_results.sort(key=lambda x: x["price"])

    return all_results


if __name__ == "__main__":
    items = scrape_all_sorted("laptop")
    for item in items:
        print(item)