from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier
from Foundation import NSDictionary, NSArray

def strFromRange(r):
  return getParameterizedAttributeValue(root, "AXStringForTextMarkerRange", r).encode('utf-8')

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

  # print(root)
  endMarker = getAttributeValue(root, "AXEndTextMarker")
  nextMarker = getAttributeValue(root, "AXStartTextMarker")
  startMarker = nextMarker
  # print(nextMarker)

  # markers = NSArray.alloc().initWithObjects_(nextMarker, endMarker)
  # r = getParameterizedAttributeValue(root, "AXTextMarkerRangeForUnorderedTextMarkers", markers)
  # print(strFromRange(r))

  # nextMarker = getMarker(880)
  i = 0
  # nextMarker = getParameterizedAttributeValue(root, "AXNextTextMarkerForTextMarker", nextMarker)

  while nextMarker:
    # elem = getParameterizedAttributeValue(root, "AXUIElementForTextMarker", nextMarker)
    leftWord = strFromRange(getParameterizedAttributeValue(root, "AXLeftWordTextMarkerRangeForTextMarker", nextMarker))
    rightWord = strFromRange(getParameterizedAttributeValue(root, "AXRightWordTextMarkerRangeForTextMarker", nextMarker))

    print([leftWord, rightWord])

    nextMarker = getParameterizedAttributeValue(root, "AXNextTextMarkerForTextMarker", nextMarker)
