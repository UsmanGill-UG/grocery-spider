import scrapy
from w3lib.url import add_or_replace_parameters as aorp

from ..items import GroceryItem


# this class is get the product links
class SMarketSpider(scrapy.Spider):
    name = 'smarket_product'
    allowed_domains = ['s-kaupat.fi']

# this is product page parser
class SMarketParser(scrapy.Spider):
    name = 'smarket_item'
    
    def extract_allergens(self, response):
        return response.css('div[data-test-id="product-info-allergens"] p::text').get()

    def extract_retailer_sku(self, product_details):
        return product_details['productId']

    def extract_images(self, response):
        return response.css('div[data-test-id="product-page-container"] img::attr(src)').get()

    def extract_brand(self, url):
        return url.split('tuote/')[-1].split('-')[0]

    def extract_ean(self, response):
        return response.css('[data-test-id="product-info-ean"] span::text').get()

    def extract_name(self, response):
        return response.css('[data-test-id="product-name"]::text').get()

    def extract_price(self, response):
        return response.css('span[data-test-id="display-price"]::text').get().strip()

    def extract_storage(self, response):
        return response.css('[data-test-id="product-features-info-storage-guide"] ::text').getall()[-1]

    def extract_category(self, response):
        return response.css('[data-test-id="product-result-breadcrumbs"] ::text').getall()[1:]

    def extract_product_url(self, response):
        return response.css('meta[property="og:url"]::attr(content)').get()
    
    def extract_nutrition(self, response):
        nutrition_elements = response.css('[data-test-id="nutrients-info-content"] .tableRow')

        nutrition_data = {}

        for nutrition in nutrition_elements[1:]:
            data = nutrition.css('.cell ::text').getall()

            print('HERE: ', data)
            name = data[0]
            value = data[1]
            percentage = data[2]

            nutrition_data[name] = {
                'value' : value,
                'percentage' : percentage
            }

        return nutrition_data
    
    def extract_country(self, response):
        return response.css('[data-test-id="product-info-country"] span::text').get()

    def parse(self, response):
        item = GroceryItem()

        item['url'] = self.extract_product_url(response)
        item['category'] = self.extract_category(response)
        item['storage'] = self.extract_storage(response)
        item['allergens'] = self.extract_allergens(response)
        item['price'] = self.extract_price(response)
        item['name'] = self.extract_name(response)
        item['brand'] = self.extract_brand(item['url'])
        item['image_urls'] = self.extract_images(response)
        item['ean'] = self.extract_ean(response)
        item['nutrition'] = self.extract_nutrition(response)
        item['country'] = self.extract_country(response)

        yield item