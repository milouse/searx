# -*- coding: utf-8 -*-

"""
 Arch Linux Packages

 @website      https://www.archlinux.org/packages/
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title, content
"""

from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urljoin, urlencode

# engine dependent config
categories = ['it', 'files']
language_support = False
paging = True
base_url = 'https://www.archlinux.org/packages'

# xpath queries
xpath_results = 'table[@class="results"]/tbody/tr'
xpath_exact_results = '//div[@id="exact-matches"]/' + xpath_results
xpath_other_results = '//div[@id="pkglist-results"]//' + xpath_results
xpath_link = './td[3]/a'
xpath_content = './td[5]'


def request(query, params):
    search_url = base_url + '/?{query}'.format(query=urlencode({'q': query}))
    if params['pageno'] > 1:
        search_url += '&pageno={pageno}'.format(pageno=params['pageno'])
    params['url'] = search_url
    return params


def extract_result_from_dom(result):
    link = result.xpath(xpath_link)[0]
    href = urljoin(base_url, link.attrib.get('href'))
    title = extract_text(link)
    content = extract_text(result.xpath(xpath_content)[0])
    return {'url': href, 'title': title, 'content': content}


def response(resp):
    results = []
    already_done = []
    dom = html.fromstring(resp.text)
    # parse exact results
    for result in dom.xpath(xpath_exact_results):
        r = extract_result_from_dom(result)
        results.append(r)
        already_done.append(r['url'])
    # parse generic results
    for result in dom.xpath(xpath_other_results):
        if 'empty' in result.classes:
            continue
        r = extract_result_from_dom(result)
        if r['url'] in already_done:
            continue
        results.append(r)
    return results
