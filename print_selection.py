from common import getRootElement, findWebArea, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier
from Foundation import NSDictionary, NSArray

root = findElemWithDOMIdentifier(getRootElement(name="Safari"), "image_1")
print(elementToString(root))
startMarker = getAttributeValue(root, "AXStartTextMarker")
endMarker = getAttributeValue(root, "AXEndTextMarker")
markers = NSArray.alloc().initWithObjects_(startMarker, endMarker)
r = getParameterizedAttributeValue(root, "AXTextMarkerRangeForUnorderedTextMarkers", markers)

def strFromRange(r):
  return getParameterizedAttributeValue(root, "AXStringForTextMarkerRange", r)

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
