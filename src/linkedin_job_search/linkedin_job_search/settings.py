BOT_NAME = "linkedin_job_search"

SPIDER_MODULES = ["linkedin_job_search.spiders"]
NEWSPIDER_MODULE = "linkedin_job_search.spiders"

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 5

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

SPIDER_MIDDLEWARES = {
    "linkedin_job_search.middlewares.LinkedinJobSearchSpiderMiddleware": 543,
}

DOWNLOADER_MIDDLEWARES = {
    "linkedin_job_search.middlewares.LinkedinJobSearchDownloaderMiddleware": 543,
}

ITEM_PIPELINES = {
    "linkedin_job_search.pipelines.LinkedinJobSearchPipeline": 300,
    "linkedin_job_search.pipelines.SQLiteStorePipeline": 400,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DUPEFILTER_CLASS = "scrapy.dupefilters.RFPDupeFilter"
DUPEFILTER_DEBUG = True

DOWNLOAD_TIMEOUT = 10

RANDOMIZE_DOWNLOAD_DELAY = True

RETRY_TIMES = 10
