import bsddb3
import json
import re
import requests
from pyquery import PyQuery as pq
from urlparse import urlparse
from Queue import deque


class Scraper(object):
  def __init__(self, handlers):
    self.stack = deque()
    self.hostname = None
    self.handlers = handlers
    self.cache = bsddb3.hashopen('./cache')

  def path(self, url):
    return '%s?%s' % (urlparse(url).path, urlparse(url).query)

  def push(self, depth, url, parents=[]):
    if not self.hostname:
      self.hostname = 'http://%s' % urlparse(url).netloc

    self.stack.appendleft([depth, url, parents])


  def run(self):
    n = 0
    while len(self.stack):
      n+=1
      item = self.stack.popleft()
      depth = item[0]
      url = str(item[1])
      parents = item[2]
      print "proc: %d\t%d\t%s" % (depth, len(self.stack), url)

      if depth >= len(self.handlers):
        print 'reached max-depth %s on %s' % (depth, url)
        continue

      if url in self.cache:
        print "cache hit"
        links = json.loads(self.cache[url])
      else:
        resp = requests.get(url)
        html = resp.content
        dom = pq(html)

        handler = self.handlers[depth]
        links = handler(dom)
        self.cache[url] = json.dumps(links)



      for link in links:
        link['depth'] = depth+1
        path = link['href']
        newparents = list(parents)
        newparents.append(link)
        newurl = '%s/%s' % (self.hostname,path)
        if path:
          self.push(depth+1, newurl, newparents)
        else:
          yield newparents



def levelFactory(asel, textsel, extractor):
  def f(dom):
    aels = dom.find(asel)
    links = []
    for el in aels:
      el = pq(el)
      text = el.find(textsel).text()
      code = extractor(text)


      href = el.find('a').attr('href')
      ret = { 'href': href }
      ret.update(code)
      links.append(ret)
    return filter(bool, links)
  return f

def startendExtractorFactory(regex):
  matcher = re.compile(regex)
  def f(text):
    if not text:
      return {'code': None}
    match = matcher.search(text)
    if match:
      group = match.groups()
      if len(group) == 1 or (len(group) >= 3 and not group[2]):
        return { 'code': group[0] }
      elif len(group) >= 3:
        code = '%s-%s' % (group[0], group[2])
        return { 'code': code }
    print 'no codes from %s' % text
    return { 'code': None }
  return f


def singleExtractorFactory(regex):
  matcher = re.compile(regex)
  def f(text):
    if not text:
      return {'code': None}
    match = matcher.search(text)
    if match:
      return { 'code': match.groups()[0] }

    print 'no codes from %s' % text
    return { 'code': None}
  return f


if __name__ == '__main__':
  l1links = levelFactory('.lvl1', 'div.chapter', startendExtractorFactory('\((\w?\d+)(-(\w?\d+)\))?'))
  l2links = levelFactory('.lvl2', 'div.section', startendExtractorFactory('\((\w?\d+)(-(\w?\d+)\))?'))
  l3links = levelFactory('.lvl3', 'div.dlvl', singleExtractorFactory('^\s*(\w?\d+)\s+'))
  l4links = levelFactory('.lvl4', 'div.dlvl', singleExtractorFactory('^\s*(\w?\d+\.\d*)\s+'))
  l5links = levelFactory('.lvl5', 'div.dlvl', singleExtractorFactory('^\s*(\w?\d+\.\d*)\s+'))
  handlers = [l1links, l2links, l3links, l4links, l5links]
  scraper = Scraper(handlers)
  scraper.push(0, 'http://icd9cm.chrisendres.com/index.php?action=contents')
  hierarchies = scraper.run()
  def getcode(link):
    return link['code']
  def maphier(hierarchy):
    return map(getcode, hierarchy)


  with file('./codes.json','w') as f:

    codes = map(maphier, hierarchies)
    f.write(json.dumps(codes))

