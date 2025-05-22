from scrapy.item import Item, Field


class GroceryItem(Item):
    url = Field()
    name = Field()
    brand = Field()
    ean = Field()
    category = Field()
    image_urls = Field()
    country = Field() # country of origin
    price = Field() # will be a dict with keys: price, currency
    ingredients = Field() # will be a list of dicts with keys: name, quantity, unit
    allergens = Field()
    nutrition = Field() # will be a dict with keys: energy, fat, saturates, carbohydrates, sugars, protein, salt etc
    storage = Field()   