from scrapy import Spider, Request
import json

from ..items import GroceryItem

class SMarketMixin:
    BASE_URL = 'https://www.s-kaupat.fi/'
    API_BASE_URL = 'https://api.s-kaupat.fi/?operationName=RemoteFilteredProducts&variables='


    CATEGORIES_URL = f'{API_BASE_URL}%7B%22id%22%3A%22513971200%22%7D&' \
                   'extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22707a9c68de67bcde9' \
                   '992a5d135e696c61d48abe1a9c765ca73ecf07bd80c513f%22%7D%7D'

    PRODUCTS_API = f'{API_BASE_URL}%7B%22includeStoreEdgePricing%22%3Afalse%2C%22storeEdgeId%22%3A%22%22%2C%22facets%22%3A%5B%7B%22key%22%3A%22brandName%22%2C%22order%22%3A%22asc%22%7D%2C%7B%22key%22%3A%22labels%22%7D%5D%2C%22generatedSessionId%22%3A%221cf04ee7-f2c9-456b-bc14-ee4dd975707c%22%2C%22includeAgeLimitedByAlcohol%22%3Atrue%2C%22limit%22%3A24%2C%22queryString%22%3A%22%22%2C%22slug%22%3A%22maito-munat-ja-rasvat-0%2Fmaidot-ja-piimat%22%2C%22storeId%22%3A%22513971200%22%2C%22useRandomId%22%3Afalse%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22dc04d87ee95539d0ac6545fcce70e604b913c3e200fe4564e884a9775b11e057%22%7D%7D'

    PRODUCT_URL = f'{BASE_URL}tuote/{{slug}}/{{ean}}'

# this class is get the product links
class SMarketSpider(Spider):
    name = 'smarket_crawler'

    def parse(self, response):
        main_page_details = response.json()
        all_categories = main_page_details['data']['category']['children'][0]['children']

        # yield from (
        #     Request(
        #         url=self.start_urls,
        #         method='POST',
        #         headers=self.headers,
        #         body=json.dumps(self.get_listings_payload(category['id'])),
        #         callback=self.parse_total_pages_listings,
        #         meta={
        #             'id': category['id'],
        #             'url_path': category['url_path']
        #         },
        #         dont_filter=True
        #     ) for category in sub_categories
        # )

# this is product page parser
class SMarketParser(Spider):
    name = 'smarket_item'
    start_urls = ["https://www.s-kaupat.fi/tuote/kotimaista-kevytmaito-1-l/6414893386488"]
    
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


# this is for product API
class SMarketParserV2(Spider):
    pass
