from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from housefinder.spiders.fotocasa import FotocasaSpider
from housefinder.spiders.idealista import IdealistaSpider

process = CrawlerProcess(get_project_settings())

process.crawl(FotocasaSpider)
process.crawl(IdealistaSpider)

process.start()
