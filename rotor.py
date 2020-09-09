from common import getRootElement, findElem, elementToString, \
  getAttributeValue, getParameterizedAttributeValue, \
  findElemWithDOMIdentifier
from Foundation import NSDictionary, NSArray

if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  (options, args) = parser.parse_args()

  root = findElem(getRootElement(name=options.app),
    lambda e: getAttributeValue(e, "AXRole") == "AXWebArea")

  res = [root]
  while len(res):
    elem = res[0]
    print(elementToString(elem))
    res = getParameterizedAttributeValue(root, "AXUIElementsForSearchPredicate",
      {"AXSearchKey": "AXAnyTypeSearchKey",
      "AXResultsLimit": 1,
      "AXDirection": "AXDirectionNext",
      "AXStartElement": elem})
    if len(res) and elem == res[0]:
      print("Can't proceed!")
      break
