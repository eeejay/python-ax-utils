from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier
from Foundation import NSDictionary, NSArray

def strFromRange(r):
  return getParameterizedAttributeValue(root, "AXStringForTextMarkerRange", r)

def getMarker(index):
    marker = getParameterizedAttributeValue(root, "AXTextMarkerForIndex", index)
    markerIndex = getParameterizedAttributeValue(root, "AXIndexForTextMarker", marker)
    print("[%d] %d" % (index, markerIndex))

if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  (options, args) = parser.parse_args()

  root = findElem(getRootElement(name=options.app),
    lambda e: getAttributeValue(e, "AXIdentifier") == "First Text View" or getAttributeValue(e, "AXRole") == "AXWebArea")

  endMarker = getAttributeValue(root, "AXEndTextMarker")
  nextMarker = getAttributeValue(root, "AXStartTextMarker")

  markers = NSArray.alloc().initWithObjects_(nextMarker, endMarker)

  index = 0
  # while nextMarker:
    # leftWord = strFromRange(getParameterizedAttributeValue(root, "AXLeftWordTextMarkerRangeForTextMarker", nextMarker))
    # rightWord = strFromRange(getParameterizedAttributeValue(root, "AXRightWordTextMarkerRangeForTextMarker", nextMarker))
    # if (True):
    #   markerIndex = getParameterizedAttributeValue(root, "AXIndexForTextMarker", nextMarker)
    #   elem = getParameterizedAttributeValue(root, "AXUIElementForTextMarker", nextMarker)
    #   relativeIndex = getParameterizedAttributeValue(elem, "AXIndexForTextMarker", nextMarker)
    #   print("%d markerIndex=%d relativeIndex=%d [%s]" % (index, markerIndex, relativeIndex, elementToString(elem)))
    # print("%d [%s]" % (index, rightWord))
    # index += 1
    # nextMarker = getParameterizedAttributeValue(root, "AXNextTextMarkerForTextMarker", nextMarker)

  print("==========")
  # getMarker(12)
  # for i in range(index):
  #   getMarker(i)



# root = findElemWithDOMIdentifier(getRootElement(name="Safari"), "image_1")
# print(elementToString(root))
# startMarker = getAttributeValue(root, "AXStartTextMarker")
# endMarker = getAttributeValue(root, "AXEndTextMarker")
markers = NSArray.alloc().initWithObjects_(nextMarker, endMarker)
r = getParameterizedAttributeValue(root, "AXTextMarkerRangeForUnorderedTextMarkers", markers)
print(len(strFromRange(r)))

# nextMarker = startMarker
# index = 0
# while True:
#   nextMarker = getParameterizedAttributeValue(root, "AXNextTextMarkerForTextMarker", nextMarker)
#   leftWord = strFromRange(getParameterizedAttributeValue(root, "AXLeftWordTextMarkerRangeForTextMarker", nextMarker))
#   rightWord = strFromRange(getParameterizedAttributeValue(root, "AXRightWordTextMarkerRangeForTextMarker", nextMarker))
#   print("%d [%s] [%s] " % (index, leftWord, rightWord))
#   index += 1
#   if not nextMarker or nextMarker == endMarker:
#     break


# print "\n".join(dir(textMarker))
# for a in dir(r):
  # if "Type" in a:
  #   print a
  # print a

# print r._cfTypeID()
# print textMarker._cfTypeID()
