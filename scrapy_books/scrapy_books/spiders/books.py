import scrapy
from scrapy_books.items import ScrapyBooksItem
import re


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    #"https://books.toscrape.com/catalogue/page-49.html"
    # "https://books.toscrape.com"

    # Set pour éviter les doublons (UPC unique)
    seen_upcs = set()

    def parse(self, response):
        """Parcourt chaque livre sur la page et suit le lien vers la page détail"""
        for book in response.css("article.product_pod"):
            link = book.css("h3 a::attr(href)").get()
            if link:
                yield response.follow(link, callback=self.parse_book)

        # Pagination : lien vers la page suivante
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        upc = response.css("table.table-striped tr:nth-child(1) td::text").get()
        if upc in self.seen_upcs:
            self.logger.info(f"Duplicate book skipped: {upc}")
            return
        self.seen_upcs.add(upc)

        item = ScrapyBooksItem()
        item["upc"] = upc
        item["title"] = response.css("h1::text").get(default="Unknown")
        item["product_type"] = response.css("table.table-striped tr:nth-child(2) td::text").get(default="Unknown")

        # Prices
        price_excl = response.css("table.table-striped tr:nth-child(3) td::text").get(default="0")
        price_incl = response.css("table.table-striped tr:nth-child(4) td::text").get(default="0")
        tax = response.css("table.table-striped tr:nth-child(5) td::text").get(default="0")
        item["price_excl_tax"] = float(price_excl.replace("£", ""))
        item["price_incl_tax"] = float(price_incl.replace("£", ""))
        item["tax"] = float(tax.replace("£", ""))

        # Availability
        availability_text = response.css("table.table-striped tr:nth-child(6) td::text").get(default="0")
        match = re.search(r"\d+", availability_text)
        item["availability"] = int(match.group()) if match else 0

        # Reviews
        reviews = response.css("table.table-striped tr:nth-child(7) td::text").get(default="0")
        item["number_of_reviews"] = int(reviews)

        # Rating
        rating_class = response.css("p.star-rating").attrib.get("class").split()[-1]
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        item["rating"] = rating_map.get(rating_class, 0)

        # Category
        breadcrumb = response.css("ul.breadcrumb li a::text").getall()
        item["category"] = breadcrumb[-1].strip() if len(breadcrumb) >= 3 else "Unknown"

        # Description
        desc = response.css("#product_description + p::text").get()
        item["description"] = " ".join(desc.strip().split()) if desc else None

        # Image
        image_rel = response.css("div.carousel-inner img::attr(src), div.thumbnail img::attr(src)").get()
        item["image_url"] = response.urljoin(image_rel) if image_rel else None

        yield item
