from collections import OrderedDict
import io
from matomo_dl import matomo_config
import pathlib

def test_read():
    DATA = """
; I'm a comment
[data] ; Comments here too
value="Tea pot"
value2  =  Electric Boogaloo
scalar=42
floating=4.2
empty     = ''
missing = ; With comment
[arrays]
array[] = 10
array[] = 'coffee'
array[] =
array[] = Plugins
"""
    out = matomo_config.read(DATA.splitlines())
    assert out == OrderedDict(
        [
            (
                "data",
                OrderedDict(
                    [
                        ("value", "Tea pot"),
                        ("value2", "Electric Boogaloo"),
                        ("scalar", 42),
                        ("floating", 4.2),
                        ("empty", ""),
                        ("missing", None),
                    ]
                ),
            ),
            ("arrays", OrderedDict([("array", [10, "coffee", None, 'Plugins'])])),
        ]
    )


def test_write():
    DATA = OrderedDict(
        [
            (
                "data",
                OrderedDict(
                    [
                        ("tea", "coffee"),
                        ("coffee", 7),
                        ("mpg", "over 9000"),
                        ("fruit", "10 oranges"),
                    ]
                ),
            ),
            ("arrays", OrderedDict([("array", [10, "tepid"])])),
        ]
    )
    EXPECTED = """; <?php exit; ?> DO NOT REMOVE THIS LINE

[data]
tea = coffee
coffee = 7
mpg = over 9000
fruit = "10 oranges"

[arrays]
array[] = 10
array[] = tepid
"""
    out = io.StringIO()
    matomo_config.write(DATA, out)
    assert EXPECTED == out.getvalue()


def test_with_real_global():
    f = pathlib.Path(__file__).parent / 'reproducable/generated/global.ini.php'
    out = matomo_config.read(f.open())
    assert 'Plugins' in out
    assert 'Plugins' in out['Plugins']
    assert 'Diagnostics' in out['Plugins']['Plugins']
