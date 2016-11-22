"""Jenkins-related file system paths."""

import os

HOME = "/var/lib/jenkins"
USERS = os.path.join(HOME, "users")
PLUGINS = os.path.join(HOME, "plugins")
SECRETS = os.path.join(HOME, "secrets")
CONFIG_FILE = os.path.join(HOME, "config.xml")
ADMIN_TOKEN = os.path.join(HOME, ".admin_token")
ADMIN_PASSWORD = os.path.join(HOME, ".admin_password")
INITIAL_PASSWORD = os.path.join(SECRETS, "initialAdminPassword")
LAST_EXEC = os.path.join(HOME, "jenkins.install.InstallUtil.lastExecVersion")
UPGRADE_WIZARD = os.path.join(HOME, "jenkins.install.UpgradeWizard.state")
LEGACY_BOOTSTRAP_FLAG = os.path.join(HOME, "config.bootstrapped")
