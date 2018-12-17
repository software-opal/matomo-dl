import json
import pathlib
import subprocess
import sys
import tarfile

TESTS_FOLDER = pathlib.Path(__file__).parent
ROOT = TESTS_FOLDER.parent
CACHE = ROOT / ".cache"
REPRODUCABLE_FOLDER = TESTS_FOLDER / "reproducable"
REPRODUCABLE_TOML = REPRODUCABLE_FOLDER / "distribution.toml"
REPRODUCABLE_LOCK_TOML = REPRODUCABLE_TOML.with_suffix(".lock.toml")
REPRODUCABLE_NORM_TOML = REPRODUCABLE_TOML.with_suffix(".norm.toml")
REPRODUCABLE_GENERATED_FILES = REPRODUCABLE_FOLDER / "generated"
REPRODUCABLE_BUILD_JSON = REPRODUCABLE_GENERATED_FILES / "build.json"


GENERATED_FILE_CHECKS = {
    "vendor/composer/autoload_classmap.php": (
        REPRODUCABLE_GENERATED_FILES / "autoload_classmap.php"
    ),
    "vendor/composer/autoload_static.php": (
        REPRODUCABLE_GENERATED_FILES / "autoload_static.php"
    ),
    "config/global.ini.php": (REPRODUCABLE_GENERATED_FILES / "global.ini.php"),
}


def test_reproducable_build(cli_runner):
    from matomo_dl.__main__ import cli

    output1 = TESTS_FOLDER / "reproducable-1.tar.gz"
    output2 = TESTS_FOLDER / "reproducable-2.tar.gz"
    for output in [output1, output2]:
        if output.exists():
            output.unlink()
        build = cli_runner.invoke(
            cli,
            [
                "--cache",
                str(CACHE),
                "build",
                str(REPRODUCABLE_TOML),
                "--output",
                str(output),
            ],
        )
        assert build.exit_code == 0, build.output

    subprocess.run(
        [
            sys.executable,
            "-m",
            "diffoscope.main",
            "--text-color=always",
            "--output-empty",
            str(output1),
            str(output2),
        ],
        cwd=TESTS_FOLDER,
        check=True,
        env={
            'SOURCE_DATE_EPOCH': '1539847974',
        }
    )

    with tarfile.open(output1) as tar:
        build_info = json.load(tar.extractfile(".build.json"))
        expected_build_info = json.loads(REPRODUCABLE_BUILD_JSON.read_text())
        assert build_info == expected_build_info

        for tar_path, check_path in GENERATED_FILE_CHECKS.items():
            gened_file = b"".join(tar.extractfile(tar_path)).decode()
            target_file = check_path.read_text()
            assert gened_file == target_file
