# apollo_scraper/spiders/apollo.py

import scrapy
from scrapy_playwright.page import PageCoroutine
import os
from scrapy.exceptions import DropItem
from scrapy.spiders import Request
from twisted.internet.error import TimeoutError, DNSLookupError, ConnectionRefusedError, ConnectionLost, TCPTimedOutError
from scrapy.core.downloader.handlers.http import HttpDownloadHelper
from scrapy.spidermiddlewares.httperror import HttpError
from apollo_scraper.items import ApolloPerson # Import your Item

class ApolloSpider(scrapy.Spider):
    name = "apollo"
    start_urls = ['https://app.apollo.io/#/login']

    # TOGGLE: Set this to False to force fresh login each time
    # This will delete the saved session state file.
    reuse_login = True

    # Search parameters: can be overridden via command line -a search_terms="term1,term2"
    search_terms = ['Software Engineer', 'Data Scientist', 'Product Manager']
    current_search_index = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override email/password from settings if provided via command line
        self.apollo_email = kwargs.get('email', self.settings.get('APOLLO_EMAIL'))
        self.apollo_password = kwargs.get('password', self.settings.get('APOLLO_PASSWORD'))

        # Override search terms if provided via command line
        if 'search_terms' in kwargs:
            self.search_terms = kwargs.get('search_terms').split(',')
            self.search_terms = [term.strip() for term in self.search_terms]

        if not self.apollo_email or not self.apollo_password:
            self.logger.error("Apollo.io email and password are required. Set them in settings.py or via -a email=... -a password=...")
            raise ValueError("Missing Apollo.io credentials")

    def start_requests(self):
        context_name = "default" # Use a consistent context name for session reuse

        # Force fresh login by deleting session state file if reuse_login is False
        if not self.reuse_login:
            try:
                state_file = f"{self.name}_login_state.json" # Dynamic state file name
                if os.path.exists(state_file):
                    os.remove(state_file)
                    self.logger.info(f"🔁 Fresh login requested. Deleted stored session file: {state_file}.")
                else:
                    self.logger.info("🔁 Fresh login requested. No stored session found.")
            except Exception as e:
                self.logger.error(f"Error deleting session file: {e}")

        self.logger.info(f"Attempting login to Apollo.io with email: {self.apollo_email}")
        yield scrapy.Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_context": context_name,
                "playwright_page_coroutines": [
                    PageCoroutine("fill", 'input[name="email"]', self.apollo_email),
                    PageCoroutine("fill", 'input[name="password"]', self.apollo_password),
                    PageCoroutine("click", 'button[type="submit"]'),
                    # Wait for a prominent element that appears AFTER successful login (e.g., sidebar)
                    PageCoroutine("wait_for_selector", "div.sidebar-container", timeout=self.settings.getint('PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT'))
                ],
                "playwright_include_page": True, # Keep page object for debugging if needed
                "playwright_store_state": True # Store login state for future runs
            },
            callback=self.after_login,
            errback=self.handle_login_error # Add error handling for login request
        )

    async def after_login(self, response):
        self.logger.info("✅ Logged in successfully!")
        self.crawler.stats.inc_value('login_successful')
        # Start the first search iteration
        yield self.start_search_iteration()

    def start_search_iteration(self):
        """Initiates a search based on the next search term."""
        if self.current_search_index < len(self.search_terms):
            search_query = self.search_terms[self.current_search_index]
            self.logger.info(f"Starting search for job title/keyword: '{search_query}' (Iteration {self.current_search_index + 1}/{len(self.search_terms)})")
            self.current_search_index += 1

            # Apollo.io's search UI often involves typing into a search bar.
            # You'll need to inspect the exact selector for the search input.
            # Example: 'input[placeholder*="job title or keyword"]' or specific class/id.
            search_input_selector = 'input[placeholder*="job title or keyword"], input[data-cy="job-title-search-input"]' # Add more selectors if needed

            return scrapy.Request(
                url="https://app.apollo.io/#/people/search", # Ensure you're on the people search page
                meta={
                    "playwright": True,
                    "playwright_context": "default",
                    "playwright_page_coroutines": [
                        # Wait for the search input to be present and visible
                        PageCoroutine("wait_for_selector", search_input_selector, timeout=60000),
                        # Fill the search input with the current query
                        PageCoroutine("fill", search_input_selector, search_query),
                        # Simulate pressing Enter to trigger the search
                        PageCoroutine("press", search_input_selector, "Enter"),
                        # Wait for the results container to load after the search
                        PageCoroutine("wait_for_selector", "div.results-container", timeout=self.settings.getint('PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT'))
                    ]
                },
                callback=self.parse_people,
                errback=self.handle_page_error # Error handling for search page requests
            )
        else:
            self.logger.info("🏁 All search iterations completed. Spider finished.")
            self.crawler.stats.inc_value('total_search_iterations_completed', len(self.search_terms))

    def parse_people(self, response):
        """Parses the people search results page."""
        self.logger.info(f"Parsing people results from: {response.url}")

        # Basic check for common blocking messages (customize as needed)
        if "Access Denied" in response.text or "Rate Limit Exceeded" in response.text:
            self.logger.critical(f"⚠️ Detected access denied or rate limit on {response.url}. Please check your proxy, delays, or reconsider scraping frequency.")
            self.crawler.stats.inc_value('rate_limit_detected')
            return # Stop processing this page

        people = response.css('div.zp_RFed0') # Adjust this selector based on current Apollo.io HTML
        if not people:
            self.logger.warning(f"No contact rows found on page: {response.url}. Check selectors or if page is empty.")
            self.crawler.stats.inc_value('empty_people_page_count')
            # You might want to yield an empty item or just log and continue
            # yield {"url": response.url, "error": "No people found"}

        extracted_count_on_page = 0
        for person in people:
            # Use ItemLoader for robust parsing and cleaning
            loader = ItemLoader(item=ApolloPerson(), selector=person)

            # Adjust these CSS selectors based on current Apollo.io HTML structure
            loader.add_css('name', 'div.zp_xJ5S3::text') # Example: Name selector
            loader.add_css('title', 'div.zp_e4xZf::text') # Example: Title selector
            loader.add_css('company', 'div.zp_s6yTf::text') # Example: Company selector
            loader.add_css('email', 'a[data-cy="contact-email-link"]::attr(href)') # Example: Email link
            loader.add_css('phone', 'span.zp_L4R0X::text') # Example: Phone selector
            loader.add_css('linkedin_url', 'a.zp_FuwzY[href*="linkedin.com/in"]::attr(href)') # Example: LinkedIn URL

            item = loader.load_item()
            if item:
                yield item
                extracted_count_on_page += 1
            else:
                self.logger.debug(f"Skipping empty item from {response.url} - potential parsing issue.")

        self.crawler.stats.inc_value('extracted_people_count', extracted_count_on_page)
        self.logger.info(f"Extracted {extracted_count_on_page} people from {response.url}")

        # Pagination logic
        # Find the next page button/link. Apollo.io might use classes or specific attributes.
        # Example: 'a.apollo-pagination-next-button::attr(href)' or similar
        next_page_link = response.css('a.pagination-next::attr(href), button[data-cy="pagination-next"]::attr(href)').get()

        if next_page_link:
            self.logger.info(f"Navigating to next page: {next_page_link}")
            self.crawler.stats.inc_value('pagination_links_followed')
            yield response.follow(
                next_page_link,
                callback=self.parse_people,
                meta={
                    "playwright": True,
                    "playwright_context": "default",
                    "playwright_page_coroutines": [
                        # Wait for the results to load on the next page
                        PageCoroutine("wait_for_selector", "div.results-container", timeout=self.settings.getint('PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT'))
                    ]
                },
                errback=self.handle_page_error
            )
        else:
            self.logger.info(f"No next page found from: {response.url}. Moving to next search term or finishing.")
            self.crawler.stats.inc_value('pagination_end_reached')
            # If no more pages for the current search, start the next search iteration
            yield self.start_search_iteration()


    def handle_login_error(self, failure):
        """Handles errors specifically during the login request."""
        self.crawler.stats.inc_value('login_errors')
        self.logger.error(f"❌ Login failed! Request URL: {failure.request.url}. Error: {repr(failure)}")

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f"Login HTTP Error: Status {response.status}, Body: {response.text[:500]}...") # Log part of response body
            if response.status == 401 or response.status == 403:
                self.logger.critical("Login credentials likely incorrect or blocked. Please verify your email/password.")
        elif failure.check(TimeoutError, TCPTimedOutError):
            self.logger.error("Login request timed out. Network issue or server too slow.")
        elif failure.check(ConnectionRefusedError, ConnectionLost, DNSLookupError):
            self.logger.error("Login connection error. Check internet connection or proxy settings.")
        else:
            self.logger.error(f"Unhandled login error type: {type(failure.value).__name__}: {failure.value}")

        # Optionally, you might want to stop the spider on critical login failure
        # self.crawler.engine.close_spider(self, 'login_failed')


    def handle_page_error(self, failure):
        """Generic error handler for subsequent page requests."""
        request = failure.request
        self.crawler.stats.inc_value('page_request_errors')
        self.logger.error(f"❌ Error processing {request.url}. Failure: {repr(failure)}")

        # Log details based on error type
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f"HTTP Error {response.status} on {request.url}. Body: {response.text[:500]}...")
            if response.status == 429: # Too Many Requests
                self.logger.warning(f"Rate limited on {request.url}. Consider increasing DOWNLOAD_DELAY or improving proxy rotation.")
                self.crawler.stats.inc_value('rate_limit_hit_during_scrape')
                # You could try to re-schedule the request with a longer delay
                # yield request.copy(dont_filter=True, meta={'playwright_page_coroutines': [PageCoroutine("wait_for_timeout", 30000)]}) # Wait 30s
            elif response.status in [401, 403]: # Unauthorized/Forbidden
                self.logger.error(f"Access denied or session expired on {request.url}. Might need fresh login.")
                self.crawler.stats.inc_value('access_denied_error')
                # Consider attempting a fresh login if this happens frequently
        elif failure.check(TimeoutError, TCPTimedOutError):
            self.logger.warning(f"Request timed out for {request.url}. Network or site slowness.")
            self.crawler.stats.inc_value('request_timeout')
        elif failure.check(ConnectionRefusedError, ConnectionLost, DNSLookupError):
            self.logger.warning(f"Connection error for {request.url}. Network or proxy issue.")
            self.crawler.stats.inc_value('connection_error')
        else:
            self.logger.error(f"Unhandled error type on {request.url}: {type(failure.value).__name__}: {failure.value}")

        # If it's a non-critical error, you might want to re-schedule the request
        # yield request.copy(dont_filter=True) # Reschedule, but be careful not to loop infinitely on persistent errors
