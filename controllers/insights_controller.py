import datetime
import os
import logging

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import tba_config
from base_controller import BaseHandler, CacheableHandler

from models.insight import Insight

VALID_YEARS = [2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002]

class InsightsOverview(CacheableHandler):
    """
    Show Insights Overview
    """
    def __init__(self, *args, **kw):
        super(InsightsOverview, self).__init__(*args, **kw)
        self._cache_expiration = 60 * 60 * 24
        self._cache_key = "insights_overview"
        self._cache_version = 1

    def _render(self):
        template_values = {
            'valid_years': VALID_YEARS,
        }
        
        insight_futures = [Insight.get_by_id_async(Insight.renderKeyName(0, insight_name)) for insight_name in Insight.INSIGHT_NAMES.values()]
        for insight_future in insight_futures:
            insight = insight_future.get_result()
            if insight:
                template_values[insight.name] = insight
                        
        path = os.path.join(os.path.dirname(__file__), '../templates/insights.html')
        return template.render(path, template_values)


class InsightsDetail(CacheableHandler):
    """
    Show Insights for a particular year
    """
    def __init__(self, *args, **kw):
        super(InsightsDetail, self).__init__(*args, **kw)
        self._cache_expiration = 60 * 60 * 24
        self._cache_key = "insight_detail_{}" # (year)
        self._cache_version = 1

    def get(self, year):
        if year == '':
            return self.redirect("/insights")
        if not year.isdigit():
            return self.redirect("/error/404")
        year = int(year)
        if year not in VALID_YEARS:
            return self.redirect("/error/404")

        self._cache_key = self._cache_key.format(year)
        super(InsightsDetail, self).get(year)

    def _render(self, year):
        template_values = {
            'valid_years': VALID_YEARS,
            'selected_year': year,
        }
        
        insight_futures = [Insight.get_by_id_async(Insight.renderKeyName(year, insight_name)) for insight_name in Insight.INSIGHT_NAMES.values()]
        for insight_future in insight_futures:
            insight = insight_future.get_result()
            if insight:
                template_values[insight.name] = insight
        
        path = os.path.join(os.path.dirname(__file__), '../templates/insights_details.html')
        return template.render(path, template_values)
        if tba_config.CONFIG["memcache"]: memcache.set(memcache_key, html, 86400) 
