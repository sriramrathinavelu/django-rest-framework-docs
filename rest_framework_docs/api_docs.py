import copy
import inspect

from importlib import import_module
from django.conf import settings
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.utils.module_loading import import_string
from rest_framework.routers import BaseRouter
from rest_framework.views import APIView
from rest_framework_docs.api_endpoint import ApiEndpoint


class ApiDocumentation(object):

    def __init__(self, drf_router=None):
        self.endpoints = []
        self.drf_router = drf_router
        try:
            root_urlconf = import_string(settings.ROOT_URLCONF)
        except ImportError:
            # Handle a case when there's no dot in ROOT_URLCONF
            root_urlconf = import_module(settings.ROOT_URLCONF)
        if hasattr(root_urlconf, 'urls'):
            self.get_all_view_names(root_urlconf.urls.urlpatterns)
        else:
            self.get_all_view_names(root_urlconf.urlpatterns)

    def get_all_view_names(self, urlpatterns, parent_pattern=None):
        # construct the list of parents leading to the URLPattern
        if parent_pattern is None:
            parent_pattern = []
        for pattern in urlpatterns:
            parent_pattern_copy = copy.copy(parent_pattern)
            if isinstance(pattern, RegexURLResolver):
                drf_router = self.get_drf_router(pattern.urlconf_name)
                if drf_router:
                    self.drf_router = drf_router
                if not isinstance(pattern.urlconf_name, list):
                    if pattern._regex != "^":
                        parent_pattern_copy.append(pattern)
                self.get_all_view_names(urlpatterns=pattern.url_patterns, parent_pattern=parent_pattern_copy)
            elif isinstance(pattern, RegexURLPattern) and self._is_drf_view(pattern) and not self._is_format_endpoint(pattern):
                api_endpoint = ApiEndpoint(pattern, parent_pattern_copy, self.drf_router)
                self.endpoints.append(api_endpoint)

    def _is_drf_view(self, pattern):
        """
        Should check whether a pattern inherits from DRF's APIView
        """
        return hasattr(pattern.callback, 'cls') and issubclass(pattern.callback.cls, APIView)

    def get_drf_router(self, urlconf_name):
        """
        Get the DRF router instance in the current module.

        This implementation checks all members and pick
        out the first members that is a descedant of BaseRouter
        """
        if inspect.ismodule(urlconf_name):
            for attribute in dir(urlconf_name):
                if isinstance(getattr(urlconf_name, attribute), BaseRouter):
                    return getattr(urlconf_name, attribute)
        return None

    def _is_format_endpoint(self, pattern):
        """
        Exclude endpoints with a "format" parameter
        """
        return '?P<format>' in pattern._regex

    def get_endpoints(self):
        return sorted(
            self.endpoints,
            key=lambda x: x.name_parent,
        )
