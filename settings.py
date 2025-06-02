# settings.py

BOT_NAME = "apollo_scraper"

SPIDER_MODULES = ["apollo_scraper.spiders"]
NEWSPIDER_MODULE = "apollo_scraper.spiders"

# Obey robots.txt rules - Be mindful of Apollo.io's ToS and robots.txt
ROBOTSTXT_OBEY = False # Set to True if you want to strictly obey robots.txt, but for logged-in areas, ToS are primary.

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# This is the average number of seconds that the Scrapy downloader will wait before downloading consecutive requests.
# If you are using proxies, you might set this lower or to 0, as proxies help distribute traffic.
# DOWNLOAD_DELAY = 1 # Uncomment and adjust if you need a static delay.

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Playwright settings
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True # Run browser in headless mode (no UI)
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 90000  # 90 seconds (default is 30s) for page loading
PLAYWRIGHT_RETRY_REQUESTS = True
PLAYWRIGHT_RETRY_TIMES = 3
PLAYWRIGHT_BROWSER_POOL_SIZE = 4 # Number of browser contexts to keep alive for efficiency

# Define the user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0',
    'Mozilla/5.0 (iPad; CPU OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/83.0.4103.88 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
]

# Configure downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None, # Disable default Scrapy UA
    'apollo_scraper.middlewares.RotatingUserAgentMiddleware': 400, # Enable custom UA middleware
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750, # Enable proxy middleware if using
}

# Proxy settings (for Zyte Smart Proxy Manager)
# Replace 'YOUR_ZYTE_API_KEY' with your actual Zyte API key.
# It's highly recommended to use an environment variable for this:
# HTTPPROXY_AUTH = os.environ.get('ZYTE_API_KEY') + ':' if os.environ.get('ZYTE_API_KEY') else ''
# Or directly for testing:
HTTPPROXY_AUTH = 'YOUR_ZYTE_API_KEY:' # Your Zyte API key followed by a colon
HTTPPROXY_URL = 'http://proxy.zyte.com:8011' # Use HTTPS for HTTPS sites: 'https://proxy.zyte.com:8011'

# Retry middleware settings
RETRY_ENABLED = True
RETRY_TIMES = 5 # Number of times to retry a failed request
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429] # HTTP codes to retry on

# Item pipeline settings
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'apollo_scraper.pipelines.ApolloPipeline': 300,
}

# Export settings
# FEED_FORMAT = 'csv' # Uncomment and set to 'csv', 'json', 'jsonl' etc.
# FEED_URI = 'apollo_people.csv' # Uncomment to enable automatic export to this file.
# FEED_EXPORT_ENCODING = 'utf-8' # Good practice to specify encoding.
# You can also define specific fields and their order for CSV/JSON
# FEED_EXPORT_FIELDS = ['name', 'title', 'company', 'email', 'phone', 'linkedin_url', 'location']

# Logging settings
LOG_LEVEL = 'INFO' # Set to 'DEBUG' for more verbose output during development
LOG_FILE = 'apollo_spider.log' # Log output to a file

# User credentials (fallback, can be overridden by command line)
APOLLO_EMAIL = 'YOUR_EMAIL@example.com' # Replace with your Apollo.io email
APOLLO_PASSWORD = 'YOUR_PASSWORD_HERE' # Replace with your Apollo.io password
