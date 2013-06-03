import csv
import json
from collections import *

class Node(object):
  def __init__(self, depth, code):
    self.depth = depth
    self.code = code
    self.parent = None
    self.children = []

  def add_child(self, child):
    if child not in self.children:
      self.children.append(child)

  def search(self, code):
    return filter(lambda n: code in n.code, self.leaves)

  def find(self, code):
    nodes = filter(lambda n: n.code == code, self.leaves)
    if nodes:
      return nodes[0]
    return None

  @property
  def root(self):
    return self.parents[0]

  @property
  def description(self):
    return self.root.code2descr.get(self.code, self.code)

  @property
  def descr(self):
    return self.description

  @property
  def codes(self):
    return map(lambda n: n.code, self.leaves)

  @property
  def parents(self):
    n = self
    ret = []
    while n:
      ret.append(n)
      n = n.parent
    ret.reverse()
    return ret


  @property
  def leaves(self):
    leaves = set()
    if not self.children:
      return set([self])
    for child in self.children:
      leaves.update(child.leaves)
    return leaves

  def leaves_at_depth(self, depth):
    return filter(lambda n: n.depth == depth, self.leaves)


  @property
  def siblings(self):
    parent = self.parent
    if not parent:
      return set()
    return set(parent.children)

  def __str__(self):
    return '%s\t%s' % (self.depth, self.code)

  def __hash__(self):
    return hash(str(self))


class ICD9(Node):
  def __init__(self, codesfname, descfname=None):
    # dictionary of depth -> dictionary of code->node
    self.depth2nodes = defaultdict(dict)
    self.code2descr = {}
    super(ICD9, self).__init__(-1, 'ROOT')

    with file(codesfname, 'r') as f:
      allcodes = json.loads(f.read())
      self.process(allcodes)

    try:
      with file(descfname, 'r') as f:
        r = csv.reader(f)
        r.next()
        for line in r:
          if len(line) >= 2:
            self.code2descr[line[0]] = line[1]
    except Exception as e:
      print e
      pass

  def process(self, allcodes):
    for hierarchy in allcodes:
      self.add(hierarchy)

  def get_node(self, depth, code):
    d = self.depth2nodes[depth]
    if code not in d:
      d[code] = Node(depth, code)
    return d[code]

  def add(self, hierarchy):
    prev_node = self
    for depth, code in enumerate(hierarchy):
      node = self.get_node(depth, code)
      node.parent = prev_node
      prev_node.add_child(node)
      prev_node = node


if __name__ == '__main__':
  tree = ICD9('codes.json', 'descriptions.csv')
  counter = Counter(map(str, tree.leaves))
  import pdb
  pdb.set_trace()
