"""
Define Scrapy items for the books scraper.
"""

import scrapy


class ScrapyBooksItem(scrapy.Item):
    """Item model representing a book."""
    title = scrapy.Field()
    upc = scrapy.Field()
    product_type = scrapy.Field()
    price_excl_tax = scrapy.Field()
    price_incl_tax = scrapy.Field()
    tax = scrapy.Field()
    availability = scrapy.Field()
    number_of_reviews = scrapy.Field()
    rating = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    image_url = scrapy.Field()
