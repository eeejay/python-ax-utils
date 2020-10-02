from common import (elementToString, getAttributeValue, pythonifyValue,
                    getParameterizedAttributeValue, kEvents, dumpTree, kBasicAttributes,
                    observeNotifications, findWebArea, getRootElement, elementPID)
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

  webArea = findWebArea(root)

  # print(elementToString(webArea))

  def cb(element, notificationName, info):
    print("%s %s" % (notificationName, elementToString(element, kBasicAttributes + options.attribute)))
    if notificationName == "AXSelectedTextChanged":
      selRange = info["AXSelectedTextMarkerRange"]
      string = getParameterizedAttributeValue(element, "AXStringForTextMarkerRange", selRange)
      # print("'%s'" % string)
    elif notificationName == "AXLiveRegionChanged":
      dumpTree(element)

  observeNotifications(root, options.event or kEvents, cb)
