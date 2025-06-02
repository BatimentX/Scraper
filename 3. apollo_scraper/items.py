# items.py
import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader

def clean_text(text):
    """Strips whitespace and handles None values."""
    if text:
        return text.strip()
    return None

def clean_email_href(email_href):
    """Removes 'mailto:' prefix from email links."""
    if email_href:
        return email_href.replace('mailto:', '')
    return None

class ApolloPerson(scrapy.Item):
    """
    Defines the structure for scraped person data from Apollo.io.
    Processors apply cleaning to the extracted fields.
    """
    name = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    title = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    company = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    email = scrapy.Field(input_processor=MapCompose(clean_email_href), output_processor=TakeFirst())
    phone = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    linkedin_url = scrapy.Field(output_processor=TakeFirst())
    # Add other fields you might want to extract, e.g.:
    # website = scrapy.Field(output_processor=TakeFirst())
    # location = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
