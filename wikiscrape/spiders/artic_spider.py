import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from wikiscrape.items import ArtInfo

class ArtICSpider(BaseSpider):
    name = 'artic'
    allowed_domains = ['www.artic.edu']
    start_urls = [
        'http://www.artic.edu/aic/collections/artwork-search/results/all/object_type_s%3A%22Painting%22+AND+in_gallery%3Atrue?page=2'
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        location = 'Art Institute Chicago'

        items = hxs.select('//div[contains(@class, "results-item-container")]')
        for item in items:
            artist = item.select('.//div[@class="details"]/text()').extract()
            if artist:
                artist = artist[0].strip()

            name_span = item.select('.//div[@class="details"]//span[@class="italic"]')
            url = name_span.select('./a/@href').extract()
            if url: url = 'http://www.artic.edu%s' % url[0]

            name = name_span.select('./a/text()').extract()
            if name: name = name[0]

            if artist and name and location:
                yield ArtInfo(name=name, artist=artist, location=location, url=url)

        pager = hxs.select('//a[contains(@class, "pager-next")]/@href').extract()
        if pager:
            yield Request('http://www.artic.edu%s' % pager[0])
        
