from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from grocery_spider.spiders.smarket_spider import SmarketSpider

process = CrawlerProcess(get_project_settings())
process.crawl(SmarketSpider)
process.start()
