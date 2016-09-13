#!/usr/bin/python
import os

from charmhelpers.core.hookenv import (
    Hooks,
    relation_get,
    log,
)
from charmhelpers.core.host import (
    write_file,
    service_restart,
)

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes

from charms.layer.jenkins.plugins import Plugins
from charms.layer.jenkins.paths import HOME

PLUGINS = "credentials ssh-credentials ssh-agent gearman-plugin git-client git"

ZUUL_CONFIG = """
<hudson.plugins.gearman.GearmanPluginConfig>
  <enablePlugin>true</enablePlugin>
    <host>{}</host>
    <port>4730</port>
</hudson.plugins.gearman.GearmanPluginConfig>
"""

GERMAN_PLUGIN = os.path.join(
    HOME, "hudson.plugins.gearman.GearmanPluginConfig.xml")


class JenkinsMaster(RelationBase):
    scope = scopes.GLOBAL

    @hook("{requires:zuul}-relation-{joined}")
    def joined(self):
        """Indicate the relation is connected and install required plugins."""
        log("Installing and configuring gearman-plugin for Zuul communication")
        # zuul relation requires we install the required plugins and set the
        # address of the remote zuul/gearman service in the plugin setting.
        plugins = Plugins()
        plugins.install(PLUGINS)
        self.set_state("{relation_name}.connected")

        # Generate plugin config with address of remote unit.
        zuul_host = relation_get("private-address")
        zuul_config = ZUUL_CONFIG.format(zuul_host).encode("utf-8")
        write_file(
            GERMAN_PLUGIN, zuul_config, owner="jenkins", group="nogroup")

        # Restart jenkins so changes will take efect.
        service_restart("jenkins")

        # Trigger the extension hook to update it with zuul relation data, if
        # it's coded to do so.
        hooks = Hooks()
        hooks.execute(["extension-relation-joined"])
