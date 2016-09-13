import os

from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core import templating

from charms.layer.jenkins.paths import CONFIG_FILE, HOME

PORT = 8080


class Configuration(object):
    """Manage global Jenkins configuration."""

    # Legacy flag file used by former versions of this charm
    _legacy_bootstrap_flag = "/var/lib/jenkins/config.bootstrapped"

    def __init__(self, hookenv=hookenv, templating=templating):
        """
        @param hookenv: An object implementing the charmhelpers.core.hookenv
            API from charmhelpers (for testing).
        @param templating: An object implementing the
            charmhelpers.core.templating API from charmhelpers (for testing).
        """
        self._hookenv = hookenv
        self._templating = templating

    def _disable_splashscreen(self):
        """Disable the splash screen for 2.x releases of jenkins"""
        import pwd
        import grp
        uid = pwd.getpwnam('jenkins').pw_uid
        gid = grp.getgrnam('nogroup').gr_gid
        splash_version_ran = os.path.join(
            HOME, 'jenkins.install.InstallUtil.lastExecVersion')
        version_installed = os.path.join(
            HOME, 'jenkins.install.UpgradeWizard.state')
        if not os.path.lexists(splash_version_ran):
            host.symlink(version_installed, splash_version_ran)
            os.fchown(splash_version_ran, uid, gid)

    def bootstrap(self):
        """Generate Jenkins' config, if it hasn't done yet."""
        config = self._hookenv.config()

        # Only run on first invocation otherwise we blast
        # any configuration changes made
        if config.get("_config-bootstrapped"):
            self._hookenv.log("Jenkins was already configured, skipping")
            return

        self._hookenv.log("Bootstrapping initial Jenkins configuration")
        context = {"master_executors": config["master-executors"]}
        self._templating.render(
            "jenkins-config.xml", CONFIG_FILE, context,
            owner="jenkins", group="nogroup")
        self._disable_splashscreen()

        config["_config-bootstrapped"] = True

        self._hookenv.open_port(PORT)

    def migrate(self):
        """Migrate the boostrap flag from the legacy file to local state."""
        config = self._hookenv.config()
        if os.path.exists(self._legacy_bootstrap_flag):
            config["_config-bootstrapped"] = True
            os.unlink(self._legacy_bootstrap_flag)
