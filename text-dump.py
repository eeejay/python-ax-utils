from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier, setAttributeValue
from Foundation import NSDictionary, NSArray

root = None

def strFromRange(r):
  if (not r):
    return ""
  return getParameterizedAttributeValue(root, "AXAttributedStringForTextMarkerRange", r)

def getMarker(index):
    return getParameterizedAttributeValue(root, "AXTextMarkerForIndex", index)

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

  nextMarker = getAttributeValue(root, "AXStartTextMarker")
  startMarker = nextMarker


  while nextMarker:
    print()
    print(repr(strFromRange(getRange(startMarker, nextMarker))))
    nextMarker = getParameterizedAttributeValue(root, "AXNextTextMarkerForTextMarker", nextMarker)
