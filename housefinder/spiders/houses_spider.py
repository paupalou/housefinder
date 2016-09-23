import scrapy
from housefinder.items import HouseItem


class HousesSpider(scrapy.Spider):
    name = 'houses'
    page_counter = 1
    start_urls = [
        'http://www.idealista.com/venta-viviendas/palma-de-mallorca-balears-illes/'
    ]

    def text(self, container, rule):
        try:
            return container.xpath(rule+'/text()').extract_first().strip()
        except AttributeError:
            return ''

    def exists_next_page(self, page):
        self.page_counter += 1
        return len(page.xpath('//li[@class="next"]')) > 0

    def parse(self, response):
        main = response.xpath('//div[@id="main-content"]').css(
                '.items-container'
                )
        houses = main.xpath('.//article[not(@class)]')

        for house in houses:
            info = house.css('.item-info-container')

            item = HouseItem()
            item['id'] = house.xpath('div/@data-adid').extract_first()
            item['name'] = self.text(info, 'a')
            item['price'] = self.text(info, './/span[@class="item-price"]')
            item['rooms'] = self.text(info, 'span[@class="item-detail"][1]')
            item['meters'] = self.text(info, 'span[@class="item-detail"][2]')
            item['floor'] = self.text(info, 'span[@class="item-detail"][3]')
            item['link'] = "https://www.idealista.com/inmueble/{}/".format(
                item['id']
            )
            yield item

        if self.page_counter < 50 and self.exists_next_page(response):
            next_page_anchor = response.xpath('//li[@class="next"]/a/@href')
            next_page = response.urljoin(next_page_anchor.extract_first())
            yield scrapy.Request(next_page, callback=self.parse)
