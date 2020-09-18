from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier
from Foundation import NSDictionary, NSArray

if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  parser.add_option("--search-key", action="store", type="string", help="Search Key", default="AXHeadingSearchKey")
  parser.add_option("--limit", action="store", type="int", help="Search Limit", default=-1)
  (options, args) = parser.parse_args()

  root = findElem(getRootElement(name=options.app),
    lambda e: getAttributeValue(e, "AXRole") == "AXWebArea")

  res = getParameterizedAttributeValue(root, "AXUIElementsForSearchPredicate",
    {"AXSearchKey": options.search_key,
    "AXResultsLimit": options.limit,
    "AXDirection": "AXDirectionNext"})

  for elem in res:
    print elementToString(elem)
