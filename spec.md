This library/executable provides a deterministic way of building a Matomo 
distribution with the customisations desired. 

This includes removing files that are not intended to make it to the server, 
and installing the plugins offline to facilitate read-only deployments.

`distribution.toml`
===================

The entire process is controlled using a `distribution.toml` file:

```toml
version = "*"
# version = "3.*"
# version = "~=3.5"

php = "7.0"
# php = "5.3"

license_key = "abcdef..."
# license_key = "$my_license_env"
# license_key = "<./my_license_file"

[plugins]
my_plugin = "*"
my_other_plugin = "1.2.4"

custom_plugin = {
  git = "https://github.com/me/my_matomo_plugin"
  ref = "master"
  # ref = "v1.2.2"
  # ref = "123abc"
}
custom_other_plugin = {
  link = "https://my-site.com/my_plugin.zip"
}

[customisation]
regenerate_manifest=true

[customisation.remove]
example_plugins=true
vendored_extras=true
documentation=true
build_support=true
tests=true
git_support=true

[customisation.update]
cacert=true

[config.plugins]
delete_examples = true
add_installed = true
delete_marketplace = true
delete_professional_services = true

[config.plugins_installed]
add_plugins = true
add_installed = true

```

Versions are a best-effort using the same schematics as `pip` with some exceptions:

- `*` -- use what ever version is latest.
- A string without a `*` or `=` symbol -- use that exact string.

`distribution.lock.toml`
========================

```toml
[matomo]
version = "1.2.3"
link = "https://dl.matomo.org/releases/1.2.3.zip"
hash = "sha512:abc123..."

[license_key]
hash = "sha512:abc123..."

[plugin.my_plugin]
version = "1.2.3"
link = "https://dl.matomo.org/releases/my_plugin/1.2.3.zip"
hash = "sha512:abc123..."

[plugin.custom_plugin]
git = "https://github.com/me/my_matomo_plugin"
ref = "abc123def456..."
hash = "sha512:abc123..."

[plugin.custom_other_plugin]
link = "https://my-site.com/my_plugin.zip"
hash = "sha512:abc123..."
```

This lockfile must be generated before the output tarball can be made. Any 
changes in hash must fail until the lockfile is updated again.

Hashing a directory is done by hashing a case-insensitive sorted tarball of the
directory.

Caching is not part of the specification.
