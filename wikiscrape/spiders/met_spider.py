import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from wikiscrape.items import ArtInfo

RE_DATE = re.compile(r'^Date:')
RE_ACCESSION = re.compile(r'^Accession Number:')
RE_ARTIST = re.compile(r'(.*?) \(.*\)')

class MetSpider(BaseSpider):
    name = 'met'
    allowed_domains = ['www.metmuseum.org']
    start_urls = [
        'http://www.metmuseum.org/collections/search-the-collections?pg=1&amp;rpp=60&amp;what=Paintings&amp;ft=*&od=on&noqs=true'
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        items = hxs.select('//ul[contains(@class, "artefact-listing")]/li')

        for item in items:
            ps = item.select('./div[@class="text-box"]/p')
            name = ps[0].select('./a/text()').extract()
            if name:
                name = name[0]

                url = ps[0].select('./a/@href').extract()
                if url: url = 'http://www.metmuseum.org%s' % url[0]

                artist = None
                for i, p in enumerate(ps[1:]):
                    p_text = p.select('./text()').extract()
                    if p_text:
                        p_text = p_text[0]
                    else:
                        continue

                    if RE_DATE.search(p_text):
                        if artist:
                            yield ArtInfo(name=name, artist=artist, location='Metropolitan Museum of Art', url=url)
                        break
                    elif RE_ACCESSION.search(p_text):
                        if artist:
                            yield ArtInfo(name=name, artist=artist, location='Metropolitan Museum of Art', url=url)
                        break
                    elif i==0:
                        artist = p_text
                        md = RE_ARTIST.search(artist)
                        if md:
                            artist = md.groups()[0]
                    else:
                        break

        next_url = hxs.select('//ul[@class="pagination"]/li[@class="next"]/a/@href').extract()
        if next_url:
            next_url = next_url[0].replace('&amp;', '&')
            yield Request('http://www.metmuseum.org%s' % next_url)
