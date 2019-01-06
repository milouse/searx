# coding: utf8

import re
import requests
from lxml import html

name = 'Dictionnaire des synonymes'
description = 'Cherche des synonymes et des antonymes sur le DES du CRISCO'
default_on = False
preference_section = 'engines'


def post_search(request, search):
    query = search.search_query.query.split(b' ')
    if len(query) < 2:
        return True
    loq = str(query[0].lower(), 'utf-8')
    loterm = str(query[1].lower(), 'utf-8')
    search_type = None

    if re.match('^(?:syn|s[iy]non[iy]me?s?)$', loq):
        search_type = 'syno'
    elif re.match('^anton[iy]me?s?$', loq):
        search_type = 'anto'
    elif re.match('^[ée]th?[iy]molog[iy]e?$', loq):
        cnrtl_url = 'http://www.cnrtl.fr/etymologie/' + loterm
        r = requests.get(cnrtl_url)
        dom = html.fromstring(r.text)
        term = dom.xpath('//li[@id="vitemselected"]/a/span/text()')
        term_type = dom.xpath('//li[@id="vitemselected"]/a/text()')
        prefix = dom.xpath('//li[@id="vitemselected"]')[0].text_content()
        article = dom.xpath('//div[@id="art"]')[0].text_content().strip()
        content = re.sub("^{}".format(prefix), '', article)
        search.result_container.infoboxes.append({
            'id': cnrtl_url,
            'infobox': term[0] + term_type[0],
            'content': content,
            'urls': [{'title': '{term} sur le CNRTL'.format(term=loterm),
                      'url': cnrtl_url}]
        })
        return True
    if search_type is None:
        return True
    # For now, we support only the first other word.
    crisco_url = 'http://crisco.unicaen.fr/des/synonymes/' + loterm
    r = requests.get(crisco_url)
    data = r.text.split("\n")
    syn_re = re.compile('<a href="/des/synonymes/(?:[^"]+)">([^<]+)</a>')

    search.result_container.infoboxes.append({
        'id': crisco_url,
        'infobox': u'Dictionnaire Électronique des Synonymes',
        'img_src': 'http://www.unicaen.fr/jsp/styles/defaut/'
                   'structures/img/bandeau_crisco.jpg',
        'content': 'Les {kind}nymes proposés en exemple ou en '
                   'suggestions sont issus du Dictionnaire Électronique'
                   ' des Synonymes édité par le Centre de Recherche '
                   'Inter-langues sur la Signification en Contexte de '
                   'l\'Université de Caen'.format(kind=search_type),
        'urls': [{'title': '{term} sur le DES'.format(term=loterm),
                  'url': crisco_url}]
    })

    if search_type == 'anto':
        i = 0
        antos = None
        for line in data:
            i += 1
            ls = line.strip()
            if ls.endswith('<!-- Fin titre (nb d\'antonymes)-->'):
                antos = data[i]
                break
        if antos is None:
            return True
        search.result_container.suggestions.update(syn_re.findall(antos))
        return True

    # Search type is 'syn'
    xdata = []
    syns = None
    for line in data:
        ls = line.strip()
        if ls == '':
            continue
        xdata.append(ls)
        if ls.endswith('<!-- Fin titre (vedette + nb de synonymes)-->'):
            syns = len(xdata)
    if syns is None:
        return True
    dom = html.fromstring("\n".join(xdata))
    syns = syn_re.findall(xdata[syns])
    best_syns = dom.xpath('//div[@id="synonymes"]/table//td/a/text()')
    final_syns = []
    for syn in best_syns:
        s = syn.strip()
        final_syns.append(s)
        syns.remove(s)
    search.result_container.answers.add(", ".join(final_syns))
    search.result_container.suggestions.update(syns)
    return True
