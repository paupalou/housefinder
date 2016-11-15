from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from housefinder.spiders.provider1 import Provider1Spider
from housefinder.spiders.provider2 import Provider2Spider

process = CrawlerProcess(get_project_settings())

process.crawl(Provider1Spider)
process.crawl(Provider2Spider)

process.start()
