from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier, kBasicAttributes
from Foundation import NSDictionary, NSArray

if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  parser.add_option("-k", "--search-key", action="append", help="Search Key", default=[])
  parser.add_option("--search-text", action="store", type="string", help="Search Text", default=None)
  parser.add_option("--limit", action="store", type="int", help="Search Limit", default=-1)
  parser.add_option("--immediate", action="store_true", help="Show immediate children only", default=False)
  parser.add_option("--previous", action="store_true", help="Search backwards", default=False)
  parser.add_option("--loop", action="store_true", help="Use loop wit start element", default=False)

  (options, args) = parser.parse_args()

  root = findElem(getRootElement(name=options.app),
    lambda e: getAttributeValue(e, "AXRole") == "AXWebArea")

  search_key = options.search_key if len(options.search_key) else "AXAnyTypeSearchKey"

  # root = getAttributeValue(root, "AXChildren")[0]
  # root = getAttributeValue(root, "AXChildren")[0]
  # root = getAttributeValue(root, "AXChildren")[0]
  #  start_elem = getAttributeValue(root, "AXChildren")[0]

  print elementToString(root, attributes=kBasicAttributes+["AXDOMIdentifier"])
  print "==="

  res = []

  params = {
    "AXSearchKey": search_key,
    "AXDirection": "AXDirectionPrevious" if options.previous else "AXDirectionNext",
    "AXResultsLimit": options.limit,
    "AXImmediateDescendantsOnly": options.immediate
  }

  if options.search_text:
    params["AXSearchText"] = options.search_text

  if options.loop:
    params["AXResultsLimit"] = 1
    r = getParameterizedAttributeValue(
      root, "AXUIElementsForSearchPredicate", params)
    while len(r):
      res.append(r[0])
      params["AXStartElement"] = r[0]
      r = getParameterizedAttributeValue(
        root, "AXUIElementsForSearchPredicate", params)

  else:
    res = getParameterizedAttributeValue(
      root, "AXUIElementsForSearchPredicate", params)

  for elem in (res or []):
    print elementToString(elem, attributes=kBasicAttributes)
