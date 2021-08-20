from common import (elementToString, getAttributeValue, pythonifyValue,
                    getParameterizedAttributeValue, kEvents, dumpTree, kBasicAttributes,
                    observeNotifications, findWebArea, getRootElement, elementPID, stopObserving, getAttributeNames)
from pprint import pprint

if __name__ == "__main__":
  from optparse import OptionParser

  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  parser.add_option("-e", "--event", action="append", default=[], help="Events")
  parser.add_option("-w", "--web", action="store_true", help="Only output web area subtree", default=False)
  parser.add_option("-a", "--attribute", action="append", default=[], help="Show provided attributes")

  (options, args) = parser.parse_args()

  root = getRootElement(name=options.app)
  if options.web:
    root = findWebArea(root)

  # print(elementToString(webArea))

  def cb(element, notificationName, info):
    # print("%s %s" % (notificationName, elementToString(element, getAttributeNames(element))))
    print("\n==\n%s %s" % (notificationName, elementToString(element, kBasicAttributes + options.attribute, all_attributes=False, cb=lambda e: ["child count", len(getAttributeValue(e, "AXChildren") or [])], compact=True)))
    parent = getAttributeValue(element, "AXParent")
    while parent:
      print "+" + elementToString(parent, kBasicAttributes + options.attribute)
      parent = getAttributeValue(parent, "AXParent")
    dumpTree(element, kBasicAttributes + options.attribute, max_depth=4)


    if notificationName == "AXSelectedTextChanged" and info:
      print(info)
      selRange = getAttributeValue(element, "AXSelectedTextMarkerRange")
      startMarker = getParameterizedAttributeValue(element, "AXStartTextMarkerForTextMarkerRange", selRange)
      # selLength = getParameterizedAttributeValue(element, "AXLengthForTextMarkerRange", selRange)
      # fromStart = getParameterizedAttributeValue(element, "AXTextMarkerRangeForUnorderedTextMarkers",
      #   [getAttributeValue(element, "AXStartTextMarker"), startMarker])
      # strStartLength = getParameterizedAttributeValue(element, "AXStringForTextMarkerRange", fromStart)
      # print("length %d from start: %s" % (selLength, strStartLength))
#      prevMarker = getParameterizedAttributeValue(element, "AXPreviousTextMarkerForTextMarker", startMarker)
      # el = getParameterizedAttributeValue(element, "AXUIElementForTextMarker", startMarker)
      # el = info["AXTextChangeElement"]
      # print("'%s'" % elementToString(el, kBasicAttributes + ["AXEditableAncestor", "AXFocusableAncestor"], compact=True))
    elif notificationName == "AXSelectedChildrenChanged":
      dumpTree(element, kBasicAttributes + options.attribute, max_depth=4)

  observeNotifications(root, options.event or kEvents, cb)
