# Scrapy settings for wikiscrape project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'artchart.info_wikiscrape'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['wikiscrape.spiders']
NEWSPIDER_MODULE = 'wikiscrape.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
