from common import getRootElement, findWebArea, dumpTree, kBasicAttributes, findElem, getAttributeValue

if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("--app", action="store", type="string", help="Target app", default="Nightly")
  parser.add_option("-a", "--attribute", action="append", default=[], help="Show provided attributes")
  parser.add_option("-w", "--web", action="store_true", help="Only output web area subtree", default=False)
  parser.add_option("--actions", action="store_true", help="Show actions", default=False)
  parser.add_option("--all-attributes", action="store_true", help="Dsiplay all attributes", default=False)
  parser.add_option("--list-attributes", action="store_true", help="List attributes", default=False)
  parser.add_option("--list-param-attributes", action="store_true", help="List parameterized attributes", default=False)
  parser.add_option("--max-depth", action="store", type="int", help="Max depth to print", default=-1)
  parser.add_option("--dom-identifier", action="store", type="string", help="AXDOMIdentifier of root", default=None)
  parser.add_option("-c", "--compact", action="store_true", help="Print each node on a line", default=False)

  (options, args) = parser.parse_args()

  root = getRootElement(name=options.app)
  if options.web:
    root = findWebArea(root)

  if options.dom_identifier:
    root = findElem(root, lambda e: getAttributeValue(e, "AXDOMIdentifier") == options.dom_identifier)

  if root:
    dumpTree(root,
      kBasicAttributes + options.attribute,
      options.actions,
      options.list_attributes,
      options.list_param_attributes,
      options.all_attributes,
      max_depth=options.max_depth,
      compact=options.compact)
  else:
    print "no root"
