#!/usr/bin/python

from charms.reactive import RelationBase
from charms.reactive import scopes


class JenkinsExtension(RelationBase):
    scope = scopes.GLOBAL

    # TODO: actually implement the consumer side.
