import logging
import shutil

from matomo_dl import matomo_config
from matomo_dl.bundle.customisation.config import logger, update_plugins_list
from matomo_dl.bundle.info import BuildInformation
from .fixtures import with_extracted_matomo


def test_base_install_generates_good_config():
    logger.setLevel(logging.DEBUG)
    with with_extracted_matomo("3.6.1") as dir_name:
        for plugin in ["ExampleAPI", "ExamplePlugin"]:
            shutil.rmtree(dir_name / "plugins" / plugin)
        info = BuildInformation(lockfile=None, customisations=None, folder=dir_name)
        update_plugins_list(info)
        config = (dir_name / "config/global.ini.php").read_text()
        assert "ExamplePlugin" not in config

        data = matomo_config.read(config.splitlines())
        plugins = data["Plugins"]["Plugins"]
        installed = data["PluginsInstalled"]["PluginsInstalled"]
        assert "ExamplePlugin" not in plugins
        assert "ExampleAPI" not in plugins
        assert "BulkTracking" in plugins

        assert "BulkTracking" not in installed
        assert "Diagnostics" in installed
        assert "UserId" in installed

        # Check for duplicates
        assert sorted(installed) == sorted(set(installed))
        assert sorted(plugins) == sorted(set(plugins))
