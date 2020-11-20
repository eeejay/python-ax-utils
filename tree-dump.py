from common import getRootElement, findWebArea, dumpTree, kBasicAttributes

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
  (options, args) = parser.parse_args()

  root = getRootElement(name=options.app)
  if options.web:
    root = findWebArea(root)

  if root:
    dumpTree(root,
      kBasicAttributes + options.attribute,
      options.actions,
      options.list_attributes,
      options.list_param_attributes,
      options.all_attributes,
      max_depth=3)
  else:
    print "no root"