# middlewares.py
from scrapy import signals
import random

class RotatingUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        # Get user agents from settings
        user_agents = crawler.settings.getlist('USER_AGENTS')
        s = cls(user_agents)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info(f"Using {len(self.user_agents)} rotating user agents.")

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        spider.logger.debug(f"Assigned User-Agent: {user_agent} to {request.url}")# middlewares.py
from scrapy import signals
import random

class RotatingUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        # Get user agents from settings
        user_agents = crawler.settings.getlist('USER_AGENTS')
        s = cls(user_agents)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info(f"Using {len(self.user_agents)} rotating user agents.")

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        spider.logger.debug(f"Assigned User-Agent: {user_agent} to {request.url}")
