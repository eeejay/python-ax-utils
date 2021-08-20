import os
import re
import json
from pprint import pformat

from ApplicationServices import (AXObserverAddNotification, AXObserverCreateWithInfoCallback,
                                 AXObserverGetRunLoopSource, AXUIElementRef,
                                 AXUIElementCopyAttributeNames,
                                 AXUIElementCopyParameterizedAttributeNames,
                                 AXUIElementCopyAttributeValue,
                                 AXUIElementIsAttributeSettable,
                                 AXUIElementCopyParameterizedAttributeValue,
                                 AXUIElementCreateApplication, AXValueGetType,
                                 AXUIElementCopyActionNames,
                                 AXUIElementSetAttributeValue,
                                 AXValueRef, kAXValueCFRangeType,
                                 kAXValueCGPointType, kAXValueCGRectType,
                                 kAXValueCGSizeType)
from Cocoa import (NSArray, NSPointFromString, NSRangeFromString,
                   NSRectFromString, NSSizeFromString, NSDictionary, NSURL)
from objc import callbackFor, callbackPointer, pyobjc_unicode
from Quartz import (CFFileDescriptorCreate,
                    CFFileDescriptorCreateRunLoopSource,
                    CFFileDescriptorEnableCallBacks, CFRunLoopAddSource,
                    CFRunLoopGetCurrent, CFRunLoopRun, CFRunLoopStop,
                    CGWindowListCopyWindowInfo, kCFFileDescriptorReadCallBack,
                    kCFRunLoopCommonModes, kCFRunLoopDefaultMode,
                    kCGNullWindowID, kCGWindowListExcludeDesktopElements)
from PyObjCTools import Conversion

kBasicAttributes = ["AXRole", "AXTitle", "AXDescription", "AXValue"]

kEvents = ["AXMainWindowChanged", "AXFocusedWindowChanged",
    "AXFocusedUIElementChanged", "AXApplicationActivated",
    "AXApplicationDeactivated", "AXApplicationHidden", "AXApplicationShown",
    "AXWindowCreated", "AXWindowMoved", "AXWindowResized", "AXWindowMiniaturized",
    "AXWindowDeminiaturized", "AXDrawerCreated", "AXSheetCreated",
    "AXHelpTagCreated", "AXValueChanged", "AXUIElementDestroyed",
    "AXElementBusyChanged", "AXMenuOpened", "AXMenuClosed", "AXMenuItemSelected",
    "AXRowCountChanged", "AXRowExpanded", "AXRowCollapsed",
    "AXSelectedCellsChanged", "AXUnitsChanged", "AXSelectedChildrenMoved",
    "AXSelectedChildrenChanged", "AXResized", "AXMoved", "AXCreated",
    "AXSelectedRowsChanged", "AXSelectedColumnsChanged", "AXSelectedTextChanged",
    "AXTitleChanged", "AXLayoutChanged", "AXAnnouncementRequested",
    "AXLiveRegionChanged", "AXLiveRegionCreated", "AXLoadComplete", "AXNewDocumentLoadComplete", "AXLayoutComplete", "AXElementBusyChanged"]

def valueToDict(val):
  ax_attr_type = AXValueGetType(val)
  ax_type_map = {
    kAXValueCGSizeType: float,
    kAXValueCGPointType: float,
    kAXValueCFRangeType: int,
    kAXValueCGRectType: float,
  }
  try:
    matches = re.findall(r"(?:((\w+):(\S+)))+", val.description())
    return dict([[m[1], ax_type_map[ax_attr_type](m[2])] for m in  matches])
  except KeyError:
    raise Exception('Return value not supported yet: {}'.format(val.description()))

def getRootElement(pid=0, name=""):
  wl = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID)
  for w in wl:
    p = int((w.valueForKey_('kCGWindowOwnerPID')))
    n = w.valueForKey_('kCGWindowOwnerName')
    if (pid and p == pid) or (name and n == name):
      return AXUIElementCreateApplication(p)

def getAttributeNames(elem):
  err, _attr = AXUIElementCopyAttributeNames(elem, None)
  attr = []
  if _attr:
    for attribute in _attr:
      err, settable = AXUIElementIsAttributeSettable(elem, attribute, None)
      if settable:
        attr.append(attribute + "*")
      else:
        attr.append(attribute)
  return sorted(attr)

def getParameterizedAttributeNames(elem):
  err, attr = AXUIElementCopyParameterizedAttributeNames(elem, None)
  return sorted(list(attr))

def getAttributeValue(elem, attribute):
  err, attrValue = AXUIElementCopyAttributeValue(elem, attribute, None)
  return attrValue

def isAttributeSettable(elem, attribute):
  err, result = AXUIElementIsAttributeSettable(elem, attribute, None)
  return bool(result)

def getActions(elem):
  err, result = AXUIElementCopyActionNames(elem, None)
  return sorted(list(result) if result else [])

def getParameterizedAttributeValue(elem, attribute, parameter):
  err, attrValue = AXUIElementCopyParameterizedAttributeValue(elem, attribute, parameter, None)
  return attrValue

def setAttributeValue(elem, attribute, value):
  err = AXUIElementSetAttributeValue(elem, attribute, value)

def pythonifyValue(val):
  if isinstance(val, pyobjc_unicode):
    return val
  elif isinstance(val, NSDictionary):
    keys = list(val)
    return dict(zip(keys, [pythonifyValue(val[k]) for k in keys]))
  elif isinstance(val, NSURL):
    return str(val)
  elif isinstance(val, NSArray):
    return [pythonifyValue(v) for v in list(val)]
  elif isinstance(val, AXValueRef):
    return valueToDict(val);
  elif isinstance(val, AXUIElementRef):
    return "<AXUIElement '%s'>" % getAttributeValue(val, "AXRoleDescription")
  elif repr(val).startswith("<AXTextMarkerRange "):
    return "<AXTextMarkerRange>"
  elif repr(val).startswith("<AXTextMarker "):
    return "<AXTextMarker>"
  else:
    return val

def findElem(elem, filter):
  if filter(elem):
    return elem
  children = getAttributeValue(elem, "AXChildren") or []
  for child in children:
    match = findElem(child, filter)
    if match:
      return match

  return None

def findWebArea(elem):
  return findElem(elem, lambda e: getAttributeValue(e, "AXRole") == "AXWebArea")

def findElemWithDOMIdentifier(elem, identifier):
  if getAttributeValue(elem, "AXDOMIdentifier") == identifier:
    return elem
  children = getAttributeValue(elem, "AXChildren") or []
  for child in children:
    webArea = findElemWithDOMIdentifier(child, identifier)
    if webArea:
      return webArea

  return None

def elementToObj(elem, attributes=kBasicAttributes, actions=False, list_attributes=False, list_param_attributes=False, all_attributes=False, cb=None):
  # return elem

  roleDesc = getAttributeValue(elem, "AXRoleDescription") or "unknown"
  _attributes = attributes if not all_attributes else getAttributeNames(elem)
  obj = { "PID": elementPID(elem) }
  obj["attributes"] = dict([(attr, pythonifyValue(getAttributeValue(elem, attr))) for attr in _attributes])
  if actions:
    obj["actions"] = getActions(elem)
  if list_attributes:
    obj["attributeNames"] = getAttributeNames(elem)
  if list_param_attributes:
    obj["parameterizedAttributeNames"] = getParameterizedAttributeNames(elem)
  if cb:
    key, value = cb(elem)
    obj[key] = value
  return (roleDesc, obj)

def elementToString(elem, attributes=kBasicAttributes, actions=False, list_attributes=False, list_param_attributes=False, all_attributes=False, cb=None, compact=False):
  obj = elementToObj(elem, attributes, actions, list_attributes, list_param_attributes, all_attributes, cb)
  if compact:
    return json.dumps(obj, sort_keys=True)
  return pformat(obj)

def elementPID(elem):
  try:
    return int(re.search(r"pid=(\d+)", repr(elem)).group(1))
  except:
    return 0

def dumpTree(elem, attributes=kBasicAttributes, actions=False, list_attributes=False, list_param_attributes=False, all_attributes=False, indent=0, cb=None, max_depth=-1, compact=False):
  if max_depth == 0:
    return
  obj = elementToObj(elem, attributes, actions, list_attributes, list_param_attributes, all_attributes, cb)
  s = "%s %s" % (indent * "+", json.dumps(obj, indent=None if compact else indent+2, sort_keys=True))
  print(s)
  children = getAttributeValue(elem, "AXChildren") or []
  for child in children:
    dumpTree(child, attributes, actions, list_attributes, list_param_attributes, all_attributes, indent + 1, cb, max_depth - 1, compact)

def handle_signals():
  def stop(cffd, cbt, info):
    CFRunLoopStop(CFRunLoopGetCurrent())

  r, w = os.pipe()

  cffd = CFFileDescriptorCreate(None, r, False, stop, None)
  CFFileDescriptorEnableCallBacks(cffd, kCFFileDescriptorReadCallBack)
  cfrlsrc = CFFileDescriptorCreateRunLoopSource(None, cffd, 0)
  CFRunLoopAddSource(CFRunLoopGetCurrent(), cfrlsrc, kCFRunLoopDefaultMode)

  def nop(signum, stackframe):
    pass

  import signal
  signal.set_wakeup_fd(w)
  signal.signal(signal.SIGINT, nop)
  signal.signal(signal.SIGTERM, nop)

def createCallback(callback):
  @callbackFor(AXObserverCreateWithInfoCallback)
  def cb(observer, element, notificationName, info, ptr):
    callback(element, notificationName, info)
  return cb

def observeNotifications(elem, notificationNames, callback, reactor=None):
  pid = elementPID(elem)

  err, observer = AXObserverCreateWithInfoCallback(pid, createCallback(callback), None)
  source = AXObserverGetRunLoopSource(observer)

  if reactor:
    CFRunLoopAddSource(reactor._cfrunloop, source, kCFRunLoopCommonModes)
  else:
    CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)

  for name in notificationNames:
    AXObserverAddNotification(observer, elem, name, None)

  if reactor:
    reactor.run()
  else:
    handle_signals()
    CFRunLoopRun()

def stopObserving():
  CFRunLoopStop(CFRunLoopGetCurrent())