#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import json
import logging
from restapi import Controller, Mapper, Resource
from restapi.main import start_server
from restapi.middlewares import Middleware, register_middleware
from restapi.serializers import JSONSerializer
from restapi.utils import basename


class TestMiddleware1(Middleware):
    def process_request(self, req):
        LOG.debug("This is a middleware1: Test process_request")

    def process_response(self, response):
        LOG.debug("This is a middleware1: Test process_response")
        return response


class TestMiddleware2(Middleware):
    def process_request(self, req):
        LOG.debug("This is a middleware2: Test process_request")

    def process_response(self, response):
        LOG.debug("This is a middleware2: Test process_response")
        return response


class HelloController(Controller):
    def action(self, request):
        data = json.loads(request.body)
        action = data.pop("action")
        method = getattr(self, action)
        return method(request, **data)

    def hello(self, request, name):
        LOG.debug("hello, {0}".format(name))
        return "hello, {0}\n".format(name)

    def start(self, request, **data):
        LOG.debug("Action: start,  Data: {0}".format(data))
        return "started\n"

    def stop(self, request, **data):
        LOG.debug("Action: stop,  Data: {0}".format(data))
        return "stopped\n"


class ActionController(Controller):
    def action(self, request, action=None, **kwargs):
        method = getattr(self, action)
        return method(request, **kwargs)

    def start(self, request, **kwargs):
        LOG.debug("Action: start,  kwargs: {0}".format(kwargs))
        return "started\n"

    def stop(self, request, **kwargs):
        LOG.debug("Action: start,  kwargs: {0}".format(kwargs))
        return "stopped\n"


def get_mapper():
    map = Mapper()

    hello_controller = HelloController()
    map.connect('actions', '/hello/{name}',
                controller=hello_controller,
                action='hello',
                conditions={'method': ['GET']})
    map.connect('actions', '/action',
                controller=hello_controller,
                action='action',
                conditions={'method': ['POST']})

    action_controller = Resource(ActionController(), JSONSerializer())
    map.connect('actions', '/action',
                controller=action_controller,
                action='action',
                conditions={'method': ['POST']})

    return map


if __name__ == "__main__":
    import sys
    name = basename(sys.argv[0], noext=True)
    addr = ('0.0.0.0', 10001)
    pid_file = "~/{0}.pid".format(name)

    LOG = logging.getLogger(name)
    LOG.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    LOG.addHandler(handler)

    register_middleware(TestMiddleware1)
    register_middleware(TestMiddleware2)

    start_server(get_mapper(), addr, pid_file)
