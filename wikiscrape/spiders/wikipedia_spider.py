import re

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector, XmlXPathSelector
from scrapy.http import Request

from wikiscrape.items import ArtInfo

RE_USER_PAGE = re.compile('User:')
RE_INFOBOX_PAINTING = re.compile(r'\{\{(Infobox (?:[pP]ainting|[aA]rtwork).*?)\}\}', re.S)
BASE_RE = r'\| *%s= *(.*?)\s*(?:$|\|\s*(?:\w+\s*)+=|<)'
RE_IB_NAME=re.compile(BASE_RE % 'title', re.S)
RE_IB_ARTIST=re.compile(BASE_RE % 'artist', re.S)
RE_IB_LOCATION=re.compile(BASE_RE % 'museum', re.S)

RE_BRACKETS = re.compile(r'\[\[(.*?)\]\]')
RE_ITALIC = re.compile(r"''(.*?)''")
RE_PIPES = re.compile(r'.*?\|\s*(.*)')

def clean_wiki_string(string):
    def pick_rep(match):
        md = RE_PIPES.search(match.groups()[0])
        if md:
            return md.groups()[0]
        else:
            return match.groups()[0]
    string = RE_BRACKETS.sub(pick_rep, string)
    string = RE_ITALIC.sub(r'\1', string)
    return string

class WikipediaSpider(BaseSpider):
    name = 'wikipedia'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [
        'http://en.wikipedia.org/w/api.php?action=query&list=embeddedin&eititle=Template:Infobox%20artwork&eilimit=100&eifilterredir=nonredirects&format=xml',
    ]

    def parse(self, response):
        xxs = XmlXPathSelector(response)

        eis = xxs.select('/api/query/embeddedin/ei')
        for ei in eis:
            pageid = ei.select('@pageid').extract()
            if pageid:
                yield Request('http://en.wikipedia.org/w/api.php?action=query&prop=revisions|info&pageids=%s&rvprop=content&inprop=url&format=xml' % pageid[0],
                              callback=self.parse_page_content)

        cont = xxs.select('/api/query-continue/embeddedin/@eicontinue').extract()
        if cont:
            yield Request('http://en.wikipedia.org/w/api.php?action=query&list=embeddedin&'
                          'eititle=Template:Infobox%%20artwork&eilimit=100&eifilterredir=nonredirects&format=xml&eicontinue=%s' % cont[0],
                          callback=self.parse)
        

    def parse_page_content(self, response):
        xxs = XmlXPathSelector(response)
        
        page_text = xxs.select('/api/query/pages/page/revisions/rev/text()').extract()
        if page_text:
            url = xxs.select('/api/query/pages/page/@fullurl').extract()
            if url:
                url = url[0]
            else:
                url = None

            page_text = page_text[0]
            md_full = RE_INFOBOX_PAINTING.search(page_text)
            if md_full:
                infobox = md_full.groups()[0]
                md = RE_IB_LOCATION.search(infobox)
                if md:
                    location = clean_wiki_string(md.groups()[0])

                    artist = ''
                    md_artist = RE_IB_ARTIST.search(infobox)
                    if md_artist:
                        artist = clean_wiki_string(md_artist.groups()[0])

                        name = ''
                        md_name = RE_IB_NAME.search(infobox)
                        if md_name:
                            name = clean_wiki_string(md_name.groups()[0])
                            yield ArtInfo(name=name, artist=artist, location=location, url=url)
