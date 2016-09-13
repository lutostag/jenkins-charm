#!/usr/bin/python

from charmhelpers.core.hookenv import (
    log,
    relation_ids,
    related_units,
    relation_get,
    relation_set,
    unit_get,
)

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes

from charms.layer.jenkins.credentials import Credentials
from charms.layer.jenkins.plugins import Plugins
from charms.layer.jenkins.api import Api


class JenkinsMaster(RelationBase):
    scope = scopes.GLOBAL

    @hook("{provides:jenkins-extension}-relation-{joined}")
    def joined(self):
        """Indicate the relation is connected and transmit our credentials."""
        log("Updating extension interface with up-to-date data.")

        # Fish out the current zuul address from any relation we have.
        zuul_address = None
        for rid in relation_ids("zuul"):
            for unit in related_units(rid):
                zuul_address = relation_get(
                    rid=rid, unit=unit, attribute="private-address")
                break

        credentials = Credentials()
        for rid in relation_ids("extension"):
            relation_settings = {
                "admin_username": credentials.username(),
                "admin_password": credentials.password(),
                "jenkins_url": "http://%s:8080" % unit_get("private-address"),
                "jenkins-admin-user": credentials.username(),
                "jenkins-token": credentials.token(),
            }
            relation_set(relation_id=rid, relation_settings=relation_settings)
            if zuul_address:
                relation_set(relation_id=rid, zuul_address=zuul_address)

        self.set_state("{relation_name}.connected")

    @hook("{provides:jenkins-extension}-relation-{changed}")
    def changed(self):
        """Install optional plugins."""
        # extension subordinates may request the principle service install
        # specified jenkins plugins
        log("Installing required plugins as requested by jenkins-extension "
            "subordinate.")
        plugins = Plugins()
        plugins.install(relation_get("required_plugins"))

        api = Api()
        api.wait()  # Wait for the service to be fully up
