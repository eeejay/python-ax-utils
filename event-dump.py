from common import (elementToString, getAttributeValue, pythonifyValue,
                    getParameterizedAttributeValue, kEvents,
                    observeNotifications, findWebArea, getRootElement, elementPID)
from pprint import pprint

if __name__ == "__main__":
  from optparse import OptionParser

  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  parser.add_option("-e", "--event", action="append", default=[], help="Events")
  parser.add_option("-w", "--web", action="store_true", help="Only output web area subtree", default=False)

  (options, args) = parser.parse_args()

  root = getRootElement(name=options.app)
  if options.web:
    root = findWebArea(root)

  webArea = findWebArea(root)

  print(elementToString(webArea))

  def cb(element, notificationName, info):
    print("%s %s" % (notificationName, elementToString(element)))
    # parent = getAttributeValue(element, "AXParent")
    # print("parent %s" % elementToString(parent))
    # pprint(pythonifyValue(info))
    # print("++++ %s" % elementToString(info["AXTextChangeElement"]));
    # print
    selRange = getAttributeValue(element, "AXSelectedTextMarkerRange")
    length = getParameterizedAttributeValue(element, "AXLengthForTextMarkerRange", selRange)
    string = getParameterizedAttributeValue(element, "AXStringForTextMarkerRange", selRange)
    print("[%s] %s" % (length, string))

    # selRange = getAttributeValue(element, "AXSelectedTextMarkerRange")
    # length = getParameterizedAttributeValue(webArea, "AXLengthForTextMarkerRange", selRange)
    # string = getParameterizedAttributeValue(webArea, "AXStringForTextMarkerRange", selRange)
    # print("webArea: [%s] %s" % (length, string))

  observeNotifications(root, options.event or kEvents, cb)
