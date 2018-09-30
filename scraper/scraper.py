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
    self.cache = {}

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

      for link in reversed(links):
        link['depth'] = depth+1
        path = link['href']
        newparents = list(parents)
        newparents.append(link)
        newurl = '%s/%s' % (self.hostname,path)
        if path:
          self.push(depth+1, newurl, newparents)
        else:
          print link
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
    if not match:
      print 'no codes from %s' % text
      return { 'code': None }

    group = match.groupdict()
    if group['end']:
      code = '%s-%s' % (group['start'], group['end'])
    else:
      code = group['start']
    return { 'code': code, 'descr': group['descr'] }
  return f


def singleExtractorFactory(regex):
  matcher = re.compile(regex)
  def f(text):
    if not text:
      return {'code': None}
    match = matcher.search(text)
    if match:
      group = match.groupdict()

      if group['code']:
        return dict(group)

    print 'no codes from %s' % text
    return { 'code': None}
  return f


if __name__ == '__main__':
  regex1 = '^(\d+\.\s*)?(?P<descr>[\-\d\w\s\,\.]*)\s*\((?P<start>\w?\d+)(-(?P<end>\w?\d+)\))?'
  regex2 = '^(?P<descr>[\-\d\w\s\,\.]*)\s*\((?P<start>\w?\d+)(-(?P<end>\w?\d+)\))?'
  regex3 = '^\s*(?P<code>\w?\d+(\.\d*)?)\s+(?P<descr>.*)'
  l1links = levelFactory('.lvl1', 'div.chapter', startendExtractorFactory(regex1))
  l2links = levelFactory('.lvl2', 'div.section', startendExtractorFactory(regex2))
  l3links = levelFactory('.lvl3', 'div.dlvl', singleExtractorFactory(regex3))
  l4links = levelFactory('.lvl4', 'div.dlvl', singleExtractorFactory(regex3))
  l5links = levelFactory('.lvl5', 'div.dlvl', singleExtractorFactory(regex3))
  handlers = [l1links, l2links, l3links, l4links, l5links]
  scraper = Scraper(handlers)
  scraper.push(0, 'http://icd9cm.chrisendres.com/index.php?action=contents')
  hierarchies = scraper.run()

  with file('./codes.json','w') as f:
    codes = [x for x in hierarchies]
    f.write(json.dumps(codes))

