#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 by Łukasz Langa
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""requests_robotstxt
   ------------------

   Provides a robots.txt-aware requests Session."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import requests
import robotexclusionrulesparser as robots
import six

if six.PY3:
    from urllib.parse import urlsplit
else:
    from urlparse import urlsplit


class RobotsTxtDisallowed(requests.RequestException):
    pass


class RobotsAwareSession(requests.Session):
    def __init__(self, registry=None):
        if registry is None:
            self.registry = {}
        else:
            self.registry = registry
        super(RobotsAwareSession, self).__init__()

    def _intermediate_send(self, method, url, timeout=None, proxies=None,
                           verify=None, cert=None, override_method=None,
                           override_url=None):
        req = requests.Request()
        req.method = method
        req.url = url
        req.headers = self.headers
        req.auth = self.auth
        req.cookies = self.cookies
        req.hooks = self.hooks
        prep = req.prepare()
        send_kwargs = {
            'stream': False,
            'timeout': timeout,
            'verify': verify,
            'cert': cert,
            'proxies': proxies,
            'allow_redirects': True,
        }
        resp = super(RobotsAwareSession, self).send(prep, **send_kwargs)
        self.cookies.update(resp.cookies)
        return resp

    def is_allowed(self, request, timeout=None, proxies=None,
                   verify=None, cert=None):
        rerp = self.get_rules(
            request.url, timeout=timeout, proxies=proxies,
            verify=verify, cert=cert,
        )

        if rerp is None:   # 404 - everybody welcome
            return True
        user_agent = request.headers.get('User-Agent', '')
        return rerp.is_allowed(user_agent, request.url)
    
    def get_rules(self, request_url, timeout=None, proxies=None,
                  verify=None, cert=None):
        url = urlsplit(request_url)
        robots_url = '{0}://{1}/robots.txt'.format(
            url.scheme,
            url.netloc,
        )
        
        try:
            rerp = self.registry[robots_url]
        except KeyError:
            r = self._intermediate_send(
                'GET', robots_url, timeout=timeout, proxies=proxies,
                verify=verify, cert=cert,
            )
            if r.ok:
                rerp = robots.RobotExclusionRulesParser()
                rerp.parse(r.text)
            elif r.status_code == 404:
                rerp = None
            else:
                r.raise_for_status()
            self.registry[robots_url] = rerp
            
        return rerp
         
    def send(self, request, **kwargs):
        if not isinstance(request, requests.PreparedRequest):
            raise ValueError('You can only send PreparedRequests.')
        if not self.is_allowed(request):
            raise RobotsTxtDisallowed(request.url)
        return super(RobotsAwareSession, self).send(request, **kwargs)
