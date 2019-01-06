import requests
from lxml import html

name = 'RubyDoc'
description = 'Add documentation for main ruby objects'
default_on = False
preference_section = 'engines'


def post_search(request, search):
    query = search.search_query.query.split(b' ')
    if len(query) < 2 or str(query[0].lower(), 'utf-8') != 'ruby':
        return True
    crit = str(query[1], 'utf-8')

    classes_xpath = '//div[@id="class-index"]//p[@class="class"]/a'
    modules_xpath = '//div[@id="class-index"]//p[@class="module"]/a'
    std_xpath = '//table[@class="target"]//a[@class="mature"]'

    matches = []
    # Get core class listing
    core_url = 'https://ruby-doc.org/core/'
    classes_r = requests.get(core_url)
    classes_dom = html.fromstring(classes_r.text.encode('UTF-8'))
    for link in classes_dom.xpath(classes_xpath):
        title = link.text_content()
        if title.lower() != crit.lower():
            continue
        href = '{}/{}'.format(core_url, link.attrib.get('href'))
        matches.append({'title': title, 'url': href, 'from': 'core'})

    # Get core class listing
    std_url = 'https://ruby-doc.org/stdlib/'
    help_you = {
        'io/console': ['ioconsole', 'io::console', 'console'],
        'io/nonblock': ['iononblock', 'io::nonblock', 'nonblock'],
        'io/wait': ['iowait', 'io::wait', 'wait'],
        'mutex_m': ['mutex'],
        'net/ftp': ['netftp', 'net::ftp', 'ftp'],
        'net/http': ['nethttp', 'net::http', 'http', 'net'],
        'net/imap': ['netimap', 'net::imap', 'imap'],
        'net/pop': ['netpop', 'net::pop', 'pop'],
        'net/smtp': ['netsmtp', 'net::smtp', 'smtp'],
        'net/telnet': ['nettelnet', 'net::telnet', 'telnet'],
        'open-uri': ['openuri', 'uri'],
        'racc/parser': ['raccparser', 'racc::parser', 'parser'],
        'resolv-replace': ['resolvreplace', 'resolv::replace', 'resolv'],
        'unicode_normalize': ['unicode', 'normalize', 'unicode-normalize',
                              'unicodenormalize']
    }
    std_r = requests.get(std_url + 'toc.html')
    std_dom = html.fromstring(std_r.text.encode('UTF-8'))
    for link in std_dom.xpath(std_xpath):
        title = link.text_content()
        lo_ti = title.lower()
        cri_ti = crit.lower()
        if lo_ti != cri_ti:
            if lo_ti not in help_you:
                continue
            elif cri_ti not in help_you[lo_ti]:
                continue
        href = '{}/{}'.format(std_url, link.attrib.get('href'))
        deep_r = requests.get(href)
        if deep_r.status_code != 200:
            continue
        sub_base_uri = std_url + 'libdoc/{title}/rdoc/{path}'
        found_uris = []
        already_done = []
        deep_c = html.fromstring(deep_r.text.encode('UTF-8'))
        for xp in [classes_xpath, modules_xpath]:
            for deep_l in deep_c.xpath(xp):
                lt = deep_l.text_content()
                lu = sub_base_uri.format(
                    title=title, path=deep_l.attrib.get('href'))
                if lu in already_done:
                    continue
                found_uris.append({'url': lu, 'title': lt})
                already_done.append(lu)
        if len(found_uris) > 0:
            matches.append({'title': title, 'url': href,
                            'uris': found_uris, 'from': 'std'})
    if len(matches) < 1:
        return True
    search.result_container.infoboxes = []
    for m in matches:
        box = {
            'id': m['url'],
            'infobox': m['title'],
            'img_src': 'https://ruby-doc.org/images/logo-rubydoc.gif'
        }
        if m['from'] == 'core':
            r = requests.get(m['url'])
            if r.status_code != 200:
                continue
            dom = html.fromstring(r.text.encode('UTF-8'))
            box['content'] = dom.xpath('//div[@id="description"]/p[1]')[0].text_content()
            box['urls'] = [{'url': m['url'], 'title': 'ruby-doc.org'}]
        else:
            box['urls'] = m['uris']
        search.result_container.infoboxes.append(box)
    return True
