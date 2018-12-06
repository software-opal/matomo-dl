import logging

from matomo_dl.bundle.fs_util import delete_all_matching
from matomo_dl.bundle.info import BuildInformation

logger = logging.getLogger(__name__)


def remove_example_plugins(build: BuildInformation) -> None:
    build.add_removed_files(
        delete_all_matching(
            build.folder,
            folders=[
                "plugins/ExampleAPI",
                "plugins/ExampleCommand",
                "plugins/ExamplePlugin",
                "plugins/ExampleReport",
                "plugins/ExampleSettingsPlugin",
                "plugins/ExampleTheme",
                "plugins/ExampleTracker",
                "plugins/ExampleUI",
                "plugins/ExampleVisualization",
            ],
        )
    )


def remove_build_support(build: BuildInformation) -> None:
    build.add_removed_files(
        delete_all_matching(
            build.folder,
            extensions=[".gzip", ".php4", ".feature"],
            names=[
                ".codeclimate.yml",
                ".htaccess",
                ".lfsconfig",
                ".npmignore",
                ".php_cs.dist",
                ".scrutinizer.yml",
                "behat.yml",
                "bower.json",
                "build.properties",
                "build.xml",
                "component.json",
                "composer.json",
                "composer.lock",
                "composer.travis.json",
                "couscous.yml",
                "grumphp.yml",
                "gruntfile.js",
                "installed.json",
                "karma.conf.js",
                "makefile",
                "package.json",
                "package.xml",
                "phpbench.json",
                "phpunit.xml.dist",
                "phpunit.xml",
                "protractor.conf.js",
            ],
            regexes=[r"libs/bower_components/jquery-ui/ui/jquery-ui[a-z\-.]+js"],
            folders=[
                "libs/bower_components/angular-mocks/",
                "libs/bower_components/jquery-ui/ui/i18n/",
                "libs/bower_components/sprintf/demo/",
            ],
            paths=[
                "libs/bower_components/iframe-resizer/test-main.js",
                "libs/bower_components/jScrollPane/script/demo.js",
                "libs/bower_components/jScrollPane/style/demo.css",
                "libs/bower_components/materialize/package.js",
                "libs/bower_components/ngDialog/server.js",
                "libs/bower_components/visibilityjs/index.js",
                "libs/bower_components/visibilityjs/logo.svg",
                "libs/jqplot/build_minified_script.sh",
                "plugins/AbTesting/libs/jquery-timepicker/jt.timepicker.jquery.json",
                "plugins/AbTesting/redirect/vendor/innocraft/php-experiments/docs/generateDocs.sh",
                "vendor/leafo/lessphp/lessify",
                "vendor/leafo/lessphp/package.sh",
                "vendor/leafo/lessphp/plessc",
                "vendor/pear/archive_tar/scripts/phptar.in",
                "vendor/pear/archive_tar/sync-php4",
            ],
        )
    )


def remove_documentation(build: BuildInformation) -> None:
    build.add_removed_files(
        delete_all_matching(
            build.folder,
            extensions=[".md", ".rst", ".markdown", ".log"],
            names=["license", "license.txt"],
            stems=[
                "authors",
                "changelog",
                "gnu-lgpl",
                "gpl-2.0",
                "copying",
                "gpl-3.0",
                "legalnotice",
                "license-colors",
                "license-sizzle",
                # "license",  # TODO: figure out how to keep 'plugins/Marketplace/angularjs/licensekey/'
                "mit and gpl2 licenses",
                "mit-license-history",
                "mit-license",
                "readme",
            ],
            folders=[
                "misc/composer/",
                "misc/cron/",
                "misc/others/",
                "misc/proxy-hide-piwik-url/",
            ],
            paths=[
                "misc/user/index.html",
                "misc/How to install Matomo.html",
                "vendor/pear/archive_tar/docs/Archive_Tar.txt",
                "libs/bower_components/chroma-js/LICENSE-colors",
            ],
        )
    )


def remove_vendored_extras(build: BuildInformation) -> None:
    build.add_removed_files(
        delete_all_matching(
            build.folder,
            folders=["vendor/tecnickcom/tcpdf/tools/", "vendor/twig/twig/ext/"],
        )
    )
