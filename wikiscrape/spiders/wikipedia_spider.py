import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector, XmlXPathSelector
from scrapy.http import Request

from wikiscrape.items import ArtInfo

RE_USER_PAGE = re.compile('User:')
RE_INFOBOX_PAINTING = re.compile(r'\{\{Infobox Painting')
RE_IB_NAME=re.compile(r'\| *title= *(.*?)\s*(?:\}\}|\|)', re.S)
RE_IB_ARTIST=re.compile(r'\| *artist= *(.*?)\s*(?:\}\}|\|)', re.S)
RE_IB_LOCATION=re.compile(r'\| *museum= *(.*?)\s*(?:\}\}|\|)', re.S)

class WikipediaSpider(BaseSpider):
    name = 'wikipedia'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [
        'http://en.wikipedia.org/wiki/Category:Paintings',
    ]

    def parse(self, response):
        return self.parse_category(response)

    def parse_category(self, response):
        hxs = HtmlXPathSelector(response)

        subcategories = hxs.select('//a[contains(@class, "CategoryTreeLabel")]')
        for sub_cat in subcategories:
            href = sub_cat.select('@href').extract()[0]
            yield Request('http://en.wikipedia.org%s' % href, callback=self.parse_category)

        pages = hxs.select('//div[@id="mw-pages"]//li/a')
        for page in pages:
            href = page.select('@href').extract()[0]
            if not RE_USER_PAGE.search(href):
                yield Request('http://en.wikipedia.org%s' % href.replace('wiki/', 'wiki/Special:Export/'), callback=self.parse_page_export)

    def parse_page_export(self, response):
        xxs = XmlXPathSelector(response)
        xxs.register_namespace('x', "http://www.mediawiki.org/xml/export-0.7/")
        
        page_text = xxs.select('/x:mediawiki/x:page/x:revision/x:text/text()').extract()
        if page_text:
            page_text = page_text[0]
            if RE_INFOBOX_PAINTING.search(page_text):
                md = RE_IB_LOCATION.search(page_text)
                if md:
                    location = md.groups()[0]

                    artist = ''
                    md_artist = RE_IB_ARTIST.search(page_text)
                    if md_artist:
                        artist = md_artist.groups()[0]

                    name = ''
                    md_name = RE_IB_NAME.search(page_text)
                    if md_name:
                        name = md_name.groups()[0]

                    yield ArtInfo(name=name, artist=artist, location=location)
