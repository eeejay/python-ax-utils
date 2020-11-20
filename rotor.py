from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier, kBasicAttributes
from Foundation import NSDictionary, NSArray

if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  parser.add_option("--search-key", action="store", type="string", help="Search Key", default="AXAnyTypeSearchKey")
  parser.add_option("--limit", action="store", type="int", help="Search Limit", default=-1)
  parser.add_option("--immediate", action="store_true", help="Show immediate children only", default=False)
  parser.add_option("--previous", action="store_true", help="Search backwards", default=False)
  parser.add_option("--loop", action="store_true", help="Use loop wit start element", default=False)

  (options, args) = parser.parse_args()

  root = findElem(getRootElement(name=options.app),
    lambda e: getAttributeValue(e, "AXRole") == "AXWebArea")

  # root = getAttributeValue(root, "AXChildren")[0]
  # root = getAttributeValue(root, "AXChildren")[0]
  # root = getAttributeValue(root, "AXChildren")[0]
  #  start_elem = getAttributeValue(root, "AXChildren")[0]

  print elementToString(root, attributes=kBasicAttributes+["AXDOMIdentifier"])
  print "==="

  res = []

  if options.loop:
    r = getParameterizedAttributeValue(root, "AXUIElementsForSearchPredicate",
        {"AXSearchKey": options.search_key,
         "AXResultsLimit": 1,
         "AXImmediateDescendantsOnly": options.immediate,
         "AXDirection": "AXDirectionPrevious" if options.previous else "AXDirectionNext"})
    while len(r):
      res.append(r[0])
      r = getParameterizedAttributeValue(root, "AXUIElementsForSearchPredicate",
        {"AXSearchKey": options.search_key,
         "AXResultsLimit": 1,
         "AXImmediateDescendantsOnly": options.immediate,
         "AXStartElement": r[0],
         "AXDirection": "AXDirectionPrevious" if options.previous else "AXDirectionNext"})

  else:
    res = getParameterizedAttributeValue(root, "AXUIElementsForSearchPredicate",
      {"AXSearchKey": options.search_key,
      "AXResultsLimit": options.limit,
      "AXImmediateDescendantsOnly": options.immediate,
      "AXDirection": "AXDirectionPrevious" if options.previous else "AXDirectionNext"})

  for elem in (res or []):
    print elementToString(elem, attributes=kBasicAttributes+["AXDOMIdentifier"])
