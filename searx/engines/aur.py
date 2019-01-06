# -*- coding: utf-8 -*-

"""
 Arch Linux Packages

 @website      https://aur.archlinux.org/
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title, content
"""

from json import loads
from searx.url_utils import urljoin, urlencode

# engine dependent config
categories = ['it', 'files']
language_support = False
paging = False
base_url = 'https://aur.archlinux.org/packages/'


def request(query, params):
    params['url'] = 'https://aur.archlinux.org/rpc.php' \
        '?v=5&type=search&{query}'.format(query=urlencode({'arg': query}))
    return params


def response(resp):
    results = []
    json = loads(resp.text)
    if 'results' not in json:
        return []
    for r in json['results']:
        url = urljoin(base_url, r['Name'])
        results.append({'url': url, 'title': r['Name'],
                        'content': r['Description']})
    return results
