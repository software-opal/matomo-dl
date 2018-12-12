import logging

from matomo_dl.bundle.info import BuildInformation
from matomo_dl.matomo_config import read as read_config, write as write_config

logger = logging.getLogger(__name__)


def update_plugins_list(build: BuildInformation) -> None:
    folder = build.folder
    plugins_folder = folder / "plugins"
    global_config = folder / "config/global.ini.php"
    config = read_config(global_config.open())
    all_plugins = config["Plugins"]["Plugins"]
    default_plugins = config["PluginsInstalled"]["PluginsInstalled"]
    assert isinstance(all_plugins, list)
    assert isinstance(default_plugins, list)
    installed_plugins = list(all_plugins)
    default_plugins = list(default_plugins)
    for plugin_name in all_plugins:
        plugin_folder = plugins_folder / str(plugin_name)
        plugin_json = plugin_folder / "plugin.json"
        if not plugin_folder.exists():
            logger.debug(f"Removing plugin {plugin_name}, not found at {plugin_folder}")
            installed_plugins.remove(plugin_name)
        if not plugin_json.exists():
            logger.debug(
                f"Core plugin {plugin_name}, Loading by default (plugin.json not found at {plugin_json})"
            )
            if plugin_name not in default_plugins:
                default_plugins.append(plugin_name)
    config["Plugins"]["Plugins"] = installed_plugins
    config["PluginsInstalled"]["PluginsInstalled"] = default_plugins
    write_config(config, global_config.open("w"))
