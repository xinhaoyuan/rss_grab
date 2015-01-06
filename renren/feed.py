# A parser processing result from feedretrieve3.do
from bs4 import BeautifulSoup as BS

def parse_feed_v3(feed_html):
  bs = BS(feed_html)
  items = []
  for a in bs.find_all('article'):
    current_item = {}
    current_item['id'] = a['id']
    current_item['photos'] = []

    for p in a.find_all('p'):
      if p.has_attr('class') and 'descript' in p['class']:
        current_item['desc'] = ''.join(list(p.stripped_strings))
      elif p.has_attr('class') and 'title' in p['class']:
        current_item['title'] = ''.join(list(p.stripped_strings))
      elif p.has_attr('class') and 'summary' in p['class']:
        current_item['summary'] = ''.join(list(p.stripped_strings))
    for pb in a.find_all(lambda tag: tag.name == 'div' and tag.has_attr('class') and 'photo-box' in tag['class']):
      for img in pb.find_all('img'):
        current_item['photos'].append(img['src'])
    if len(current_item['photos']) == 0:
      del current_item['photos']
    items.append(current_item)
  return items
