from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier, setAttributeValue
from Foundation import NSDictionary, NSArray

root = None

def strFromRange(r):
  if (not r):
    return ""
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

  r = getAttributeValue(root, "AXSelectedTextMarkerRange");
  print(strFromRange(r))

  # root = findElem(getRootElement(name=options.app),
  #   lambda elem: getAttributeValue(elem, "AXDOMIdentifier") == "t")

  # print(getAttributeValue(root, "AXSelectedText"))
  # setAttributeValue(root, "AXValue", "olam")
  # print(getAttributeValue(root, "AXSelectedText"))

  # # setAttributeValue(root, "AXValue", "WUUT")
  # print(getParameterizedAttributeValue(root, "AXRangeForLine", 1))
  # print(getAttributeValue(root, "AXVisibleCharacterRange"))