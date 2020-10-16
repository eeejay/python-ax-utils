from twisted.web import server, resource
from twisted.internet.cfreactor import install
from twisted.internet import endpoints
import json
import re
from pprint import pprint
from weakref import WeakSet
from common import (
    elementToString,
    getAttributeValue,
    pythonifyValue,
    isAttributeSettable,
    getParameterizedAttributeValue,
    kEvents,
    dumpTree,
    kBasicAttributes,
    getActions,
    observeNotifications,
    findElem,
    getRootElement,
    elementPID,
    observeNotifications,
)

from Quartz import (
    CFRunLoopGetCurrent,
    CFRunLoopAddCommonMode,
    CFRunLoopContainsObserver,
    CFRunLoopContainsSource,
    kCFRunLoopDefaultMode,
    kCFRunLoopCommonModes,
)

install()
from twisted.internet import reactor

INFO = {
    "ATTAname": "ATTA-OSX",
    "ATTAversion": "0.1",
    "API": "AXAPI",
    "APIversion": "1.0",
}

FAILURES = []

class StartResource(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        response = {"status": "READY"}
        response.update(INFO)
        request.setHeader(b"content-type", b"application/json")
        return json.dumps(response, indent=4, sort_keys=True)


class EndResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader(b"content-type", b"text/plain")
        return "goodbye, now"


class TestResource(resource.Resource):
    isLeaf = True

    def __init__(self, webArea, eventsPromise):
        resource.Resource.__init__(self)
        self.webArea = webArea
        self.eventsPromise = eventsPromise
        self.receivedEvents = []
        self.deferred = None
        self.elem = None

    def _assert(self, value, assertion, expected):
        _expected = expected
        try:
            _expected = json.loads(_expected)
        except:
            pass

        def _isExpected(_val):
            if _expected == "<nil>":
                return not _val or _val == "AXUnknown" or _val

            return _val == _expected

        if assertion == "is":
            if _isExpected(value):
                return {"result": "PASS"}
            return {
                "result": "FAIL",
                "message": "expected %s, got %s" % (repr(_expected), repr(value)),
            }

        if assertion == "isNot":
            if not _isExpected(value):
                return {"result": "PASS"}
            return {
                "result": "FAIL",
                "message": "didn't expected '%s', got '%s'" % (_expected, value),
            }

        if assertion == "contains":
            if hasattr(value, "__iter__") and any(_isExpected(a) for a in value):
                return {"result": "PASS"}
            return {
                "result": "FAIL",
                "message": "didn't find %s does not contain %s" % (value, _expected),
            }

        if assertion == "doesNotContain":
            if hasattr(value, "__iter__") and not any(_isExpected(a) for a in value):
                return {"result": "PASS"}
            return {"result": "FAIL", "message": "found %s in %s" % (value, _expected)}

        if assertion == "isLTE":
            if value <= _expected:
                return {"result": "PASS"}
            return {
                "result": "FAIL",
                "message": "expected %s, to be smaller or equal to %s"
                % (repr(value), repr(_expected)),
            }

        if assertion == "isGTE":
            if value >= _expected:
                return {"result": "PASS"}
            return {
                "result": "FAIL",
                "message": "expected %s, to be greater or equal to %s"
                % (repr(value), repr(_expected)),
            }

        return {
            "result": "FAIL",
            "message": "assertion type '%s' not implemented" % assertion,
        }

    def _testProperty(self, attributeName, assertion, expected):
        value = pythonifyValue(
            getAttributeValue(self.elem, attributeName.split(".")[0])
        )
        if attributeName.endswith(".length"):
            value = len(value)

        return self._assert(value, assertion, expected)

    def _testActions(self, assertion, expected):
        value = pythonifyValue(getActions(self.elem))
        return self._assert(value, assertion, expected)

    def _testAccessible(self, assertion, expected):
        return self._assert(bool(self.elem), assertion, expected)

    def _testEvent(self, assertion, expected):
        if not self.receivedEvents:
            return {"result": "FAIL", "message": "no events recieved"}

        return self._assert(self.receivedEvents[0][1], assertion, expected)

    def _testFunctionResult(self, func, assertion, expected):
        match = re.search(r"(\w+)\((\w+)\)", func)
        if match and match.group(1) == "AXUIElementIsAttributeSettable":
            return self._assert(
                isAttributeSettable(self.elem, match.group(2)), assertion, expected
            )

        return {"result": "FAIL", "message": "function not supported: %s" % func}

    def render_POST(self, request):
        self.deferred = reactor.callLater(3, self._delayedRender, request)
        if self.eventsPromise:
            self.eventsPromise.then(self._resolvedEvents)
        else:
            self.deferred.reset(0)

        return server.NOT_DONE_YET

    def _resolvedEvents(self, receivedEvents):
        self.receivedEvents = receivedEvents
        if self.deferred:
            self.deferred.reset(0)

    def _delayedRender(self, request):
        self.deferred = None
        request.setHeader(b"content-type", b"application/json")
        results = []
        r = json.loads(request.content.read().decode("utf-8"))

        def _filter(e):
            return unicode(getAttributeValue(e, "AXDOMIdentifier")) == r["id"]

        self.elem = findElem(self.webArea, _filter)

        data = r["data"]
        for i in xrange(len(r["data"])):
            assertion = data[i]
            if assertion[0] == "property" and assertion[1] == "accessible":
                results.append(self._testAccessible(*assertion[2:]))
            elif assertion[0] == "property" and assertion[1] == "actions":
                results.append(self._testActions(*assertion[2:]))
            elif assertion[0] == "property":
                results.append(self._testProperty(*assertion[1:]))
            elif assertion[0] == "result":
                results.append(self._testFunctionResult(*assertion[1:]))
            elif assertion[0] == "event":
                results.append(self._testEvent(*assertion[2:]))
            else:
                results.append(
                    {"result": "FAIL", "message": "not implemented: %s" % assertion}
                )
            # if results[-1]["result"] == "FAIL":
            #   print(assertion)
            #   print(results[-1]["message"])

        response = {"status": "OK", "statusText": "", "log": "", "results": results}

        if filter(lambda e: e["result"] != "PASS", results):
          url = getAttributeValue(self.webArea, "AXURL")
          print("=== %s" % url)
          for i in xrange(len(results)):
            if results[i]["result"] != "PASS":
              print("%s => %s" % (r["data"][i], results[i]))
              FAILURES.append({ "data": r["data"][i], "result": results[i]})
        request.write(json.dumps(response, indent=4, sort_keys=True))
        request.finish()


class EventsResource(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        response = {"status": "READY"}
        response.update(INFO)
        request.setHeader(b"content-type", b"application/json")
        return json.dumps(response, indent=4, sort_keys=True)

class FailuresResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader(b"content-type", b"application/json")
        return json.dumps(FAILURES, indent=4, sort_keys=True)


class EventPromise:
    _instances = WeakSet()

    @classmethod
    def handleNotification(cls, element, notificationName, info):
        for instance in cls._instances:
            instance.handleEvent(element, notificationName, info)

    def __init__(self, expectedEvents):
        self._expectedEvents = expectedEvents
        self._receivedEvents = []
        self._callback = None
        EventPromise._instances.add(self)

    def handleEvent(self, element, notificationName, info):
        if self._expectedEvents and self._expectedEvents[0] == notificationName:
            self._expectedEvents.pop(0)
            self._receivedEvents.append((element, notificationName, info))
            if not self._expectedEvents and self._callback:
                self._callback(self._receivedEvents)

    def then(self, callback):
        if not self._expectedEvents:
            callback(self._receivedEvents)
        else:
            self._callback = callback


class RootResource(resource.Resource):
    # isLeaf = True
    def __init__(self, appName):
        resource.Resource.__init__(self)
        self.appName = appName
        self.webArea = None
        self.url = None
        self.eventsPromise = None

    def _getWebArea(self):
        def _filter(e):
            if getAttributeValue(e, "AXRole") != "AXWebArea":
                return False
            return True

        rootElem = getRootElement(name=self.appName)
        return findElem(rootElem, _filter)

    def getChild(self, name, request):
        request.setHeader("Access-Control-Allow-Headers", "Content-Type")
        request.setHeader("Access-Control-Allow-Methods", "POST")
        request.setHeader("Access-Control-Allow-Origin", "*")
        request.setHeader("Access-Control-Expose-Headers", "Allow, Content-Type")
        request.setHeader("Allow", "POST")

        if name == "start":
            content = request.content.read().decode("utf-8")
            self.url = json.loads(content)["url"]
            self.webArea = self._getWebArea()
            if self.webArea:
                return StartResource()

        if name == "end":
            self.webArea = None
            return EndResource()

        if name == "test":
            return TestResource(self.webArea, self.eventsPromise)

        if name == "startlisten":
            content = request.content.read().decode("utf-8")
            self.eventsPromise = EventPromise(json.loads(content)["events"])
            return EventsResource()

        if name == "stoplisten":
            self.eventsPromise = None
            return EventsResource()

        if name == "failures":
          return FailuresResource()

        return resource.Resource()


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        "--app", action="store", type="string", help="Target app", default="Nightly"
    )
    parser.add_option(
        "-p", "--port", action="store", type="int", help="HTTP port", default=4119
    )

    (options, args) = parser.parse_args()

    endpoints.serverFromString(reactor, "tcp:%d" % options.port).listen(
        server.Site(RootResource(options.app))
    )

    observeNotifications(
        getRootElement(name=options.app),
        kEvents,
        EventPromise.handleNotification,
        reactor,
    )
