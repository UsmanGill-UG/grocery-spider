import scrapy
from w3lib.url import add_or_replace_parameters as aorp

from ..items import GroceryItem


# class CarhattSpider(scrapy.Spider):
#     name = 'smarket_product'
#     allowed_domains = ['s-kaupat.fi']
#     BASE_URL = 'https://www.s-kaupat.fi'
#     # PRODUCTS_URL = '{base_url}/products?sort=&size=12&brandIds=15'
#     # PRODUCT_DETAIL = '{base_url}/products/{product_id}/detail'
#     # start_urls = [f'{BASE_URL}/categories?sourceSite=CARHARTT']
#     start_urls = ['https://www.s-kaupat.fi/tuote/kotimaista-kevytmaito-1-l/6414893386488']

#     def parse(self, response):
#         category_data = response.json()

#         for item in category_data.get('payload', []):
#             if category_id := item.get('categoryId'):
#                 products_base_url = self.PRODUCTS_URL.format(base_url=self.BASE_URL)
#                 params = {
#                     'mainCategoryId': category_id,
#                     'page': '0',
#                 }
#                 products_url = add_or_replace_parameters(products_base_url, params)

#             yield scrapy.Request(
#                     products_url,
#                     callback=self.parse_products_pages,
#                     meta={'category_id': category_id}
#                 )

#     def parse_products_pages(self, response):
#         products_page_info = response.json()
#         total_pages = products_page_info['payload']['totalPages']
#         category_id = response.meta['category_id']

#         for page in range(total_pages+1):
#             products_base_url = self.PRODUCTS_URL.format(base_url=self.BASE_URL)
#             params = {
#                 'mainCategoryId': category_id,
#                 'page': str(page),
#             }
#             product_url = add_or_replace_parameters(products_base_url, params)

#             yield scrapy.Request(
#                 product_url,
#                 callback=self.parse_products,
#             )

#     def parse_products(self, response):
#         products_page = response.json()
#         products = products_page['payload']['content']
#         parser = CarhattParser()

#         for product in products:
#             product_id = product.get('productId')
#             product_detail_url = (
#                 self.PRODUCT_DETAIL.format(
#                     base_url=self.BASE_URL,
#                     product_id=product_id
#                 )
#             )

#             yield scrapy.Request(
#                 product_detail_url,
#                 callback=parser.parse,
#             )


class CarhattParser(scrapy.Spider):
    name = 'smarket_item'

    start_urls = [
        'https://www.s-kaupat.fi/tuote/kotimaista-kevytmaito-1-l/6414893386488'
    ]

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

        yield item