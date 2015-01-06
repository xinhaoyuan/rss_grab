# A parser processing result from feedretrieve3.do

from html.parser import HTMLParser

class FeedParserV3(HTMLParser):

  def __init__(self):
    HTMLParser.__init__(self)
    self._items = []
    self._current_item = None
    self._current_photo = None
    self._record_head = False
    self._record_desc = False
    self._record_photo = False
    self._record_title = False
    self._record_summary = False
    self._tag_stack = []
  
  def handle_starttag(self, tag, attrs):
    tag_class = ''
    for k, v in attrs:
      if k == 'class':
        tag_class = v
        break
    self._tag_stack.append((tag, attrs, tag_class))

    if self._current_item is None:
      if tag == 'article':
        self._current_item = {}
        for name, value in attrs:
          if name == 'id':
            self._current_item['id'] = value
    elif tag == 'h3':
      self._record_head = True
    elif tag == 'div' and 'photo-box' in tag_class:
      self._record_photo = True
      self._current_photo = {}
      if 'photos' not in self._current_item:
        self._current_item['photos'] = []
    elif tag == 'img' and self._record_photo:
      img_src = None
      for k, v in attrs:
        if k == 'src':
          img_src = v
          break
      self._current_photo['photo_src'] = img_src
    elif tag == 'p' and 'descript' in tag_class:
      self._record_desc = True
    elif tag == 'p' and 'summary' in tag_class:
      self._record_summary = True
    elif tag == 'p' and 'title' in tag_class:
      self._record_title = True

  def handle_endtag(self, tag):
    tag, attrs, tag_class = self._tag_stack.pop()
    if self._current_item is None:
      return
    elif tag == 'article':
      self._items.append(self._current_item)
      self._current_item = None
    elif tag == 'h3':
      self._record_head = False
    elif tag == 'div' and 'photo-box' in tag_class:
      self._record_photo = False
      self._current_item['photos'].append(self._current_photo)
      self._current_photo = None
    elif tag == 'p' and 'descript' in tag_class:
      self._record_desc = False
    elif tag == 'p' and 'summary' in tag_class:
      self._record_summary = False
    elif tag == 'p' and 'title' in tag_class:
      self._record_title = False

  def handle_data(self, data):
    if self._current_item is None:
      return
    elif self._record_head:
      self._current_item['head'] = self._current_item.get('head', '') + data
    elif self._record_desc:
      self._current_item['desc'] = self._current_item.get('desc', '') + data
    elif self._record_summary:
      self._current_item['summary'] = self._current_item.get('summary', '') + data
    elif self._record_title:
      self._current_item['title'] = self._current_item.get('title', '') + data
      
  def dump(self):
    return self._items
  
