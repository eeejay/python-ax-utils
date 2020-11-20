from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier
from Foundation import NSDictionary, NSArray
from pprint import pprint
import json
import re

COL_LIMIT = 80

def strFromRange(r):
  return getParameterizedAttributeValue(root, "AXStringForTextMarkerRange", r)

def getMarker(index):
    return getParameterizedAttributeValue(root, "AXTextMarkerForIndex", index)

def dictToJS(obj):
  data = []
  indent = 8;
  for e in obj:
    d = []
    for key, value in e.items():
      itemstr = "%s: %s" % (key, json.dumps(value))
      if len(itemstr) > COL_LIMIT:
        elems = (",\n%s" % (" "*(indent + 2 + len("%s: [" % key)))).join([json.dumps(elem) for elem in value])
        itemstr = "%s: [%s]" % (key, elems)
      d.append(itemstr)
    data.append("%s{ %s }" % (" "*indent, (",\n%s" % (" "*(indent + 2))).join(d)))
  return "[\n%s]" % ",\n".join(data)

def getRange(m1, m2):
  markers = NSArray.alloc().initWithObjects_(m1, m2)
  return getParameterizedAttributeValue(root, "AXTextMarkerRangeForUnorderedTextMarkers", markers)

if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  (options, args) = parser.parse_args()

  def filter(e):
    return getAttributeValue(e, "AXRole") == "AXWebArea"

  root = findElem(getRootElement(name=options.app),
    filter)

  endMarker = getAttributeValue(root, "AXEndTextMarker")
  nextMarker = getAttributeValue(root, "AXStartTextMarker")
  startMarker = nextMarker

  # markers = NSArray.alloc().initWithObjects_(nextMarker, endMarker)
  # r = getParameterizedAttributeValue(root, "AXTextMarkerRangeForUnorderedTextMarkers", markers)
  # print(strFromRange(r))

  # nextMarker = getMarker(880)
  expected = []
  words = []
  elements = []
  i = 0
  while nextMarker:
    leftWord = strFromRange(getParameterizedAttributeValue(root, "AXLeftWordTextMarkerRangeForTextMarker", nextMarker))
    rightWord = strFromRange(getParameterizedAttributeValue(root, "AXRightWordTextMarkerRangeForTextMarker", nextMarker))
    elem = getParameterizedAttributeValue(root, "AXUIElementForTextMarker", nextMarker)
    d = {}
    d["words"] = [leftWord, rightWord]
    d["element"] = [
      getAttributeValue(elem, "AXRole"),
      getAttributeValue(elem, "AXValue"),
      strFromRange(getParameterizedAttributeValue(root, "AXTextMarkerRangeForUIElement", elem))]
    d["lines"] = [
      strFromRange(getParameterizedAttributeValue(root, "AXLineTextMarkerRangeForTextMarker", nextMarker)),
      strFromRange(getParameterizedAttributeValue(root, "AXLeftLineTextMarkerRangeForTextMarker", nextMarker)),
      strFromRange(getParameterizedAttributeValue(root, "AXRightLineTextMarkerRangeForTextMarker", nextMarker))
    ]
    d["paragraph"] = strFromRange(getParameterizedAttributeValue(root, "AXParagraphTextMarkerRangeForTextMarker", nextMarker))
    d["style"] = strFromRange(getParameterizedAttributeValue(root, "AXStyleTextMarkerRangeForTextMarker", nextMarker))
    expected.append(d)

    nextMarker = getParameterizedAttributeValue(root, "AXNextTextMarkerForTextMarker", nextMarker)

  print dictToJS(expected)
