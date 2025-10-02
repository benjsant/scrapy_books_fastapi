import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy_books.items import ScrapyBooksItem
import re

# --- Fonctions de nettoyage ---
def clean_price(value: str) -> float:
    """Supprime le symbole £ et convertit en float."""
    try:
        return float(value.replace("£", "").strip())
    except (ValueError, AttributeError):
        return 0.0

def clean_availability(value: str) -> int:
    """Extrait le nombre de disponibilité à partir du texte."""
    match = re.search(r"\d+", value)
    return int(match.group()) if match else 0

def clean_description(value: str) -> str:
    """Nettoie la description en supprimant espaces multiples et caractères invisibles."""
    if not value:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"[^\x20-\x7E]+", "", value)
    return value

# --- Spider principal ---
class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    # https://books.toscrape.com/catalogue/page-49.html
    # https://books.toscrape.com
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        """Parcourt chaque livre sur la page et suit le lien vers la page détail."""
        for book in response.css("article.product_pod"):
            link = book.css("h3 a::attr(href)").get()
            if link:
                yield response.follow(link, callback=self.parse_book)

        # Pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        """Extraction détaillée d’un livre avec nettoyage via ItemLoader."""
        loader = ItemLoader(item=ScrapyBooksItem(), response=response)
        loader.default_output_processor = TakeFirst()

        # UPC
        upc = response.css("table.table-striped tr:nth-child(1) td::text").get()
        loader.add_value("upc", upc)

        # Champs simples
        loader.add_css("title", "h1::text")
        loader.add_css("product_type", "table.table-striped tr:nth-child(2) td::text")
        loader.add_css("price_excl_tax", "table.table-striped tr:nth-child(3) td::text", MapCompose(clean_price))
        loader.add_css("price_incl_tax", "table.table-striped tr:nth-child(4) td::text", MapCompose(clean_price))
        loader.add_css("tax", "table.table-striped tr:nth-child(5) td::text", MapCompose(clean_price))
        loader.add_css("availability", "table.table-striped tr:nth-child(6) td::text", MapCompose(clean_availability))
        loader.add_css("number_of_reviews", "table.table-striped tr:nth-child(7) td::text", MapCompose(int))

        # Rating
        rating_class = response.css("p.star-rating").attrib.get("class", "").split()[-1]
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        loader.add_value("rating", rating_map.get(rating_class, 0))

        # Catégorie
        breadcrumb = response.css("ul.breadcrumb li a::text").getall()
        loader.add_value("category", breadcrumb[-1].strip() if len(breadcrumb) >= 3 else "Unknown")

        # Description
        desc = response.css("#product_description + p::text").getall()
        loader.add_value("description", desc, MapCompose(clean_description), Join(" "))

        # Image
        image_rel = response.css("div.carousel-inner img::attr(src), div.thumbnail img::attr(src)").get()
        loader.add_value("image_url", response.urljoin(image_rel) if image_rel else None)

        yield loader.load_item()
