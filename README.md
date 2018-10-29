Matomo distribution manager
===========================

A command-line tool for building Matomo distributions with plugins bundled in 
and various customizations applied. It builds a bundled zip file in a 
verifiable and reproducible manner for use with systems like Docker.

Features
--------

- **Version pining**
  Whilst a range of accepted versions may be specified in the 
  `distribution.toml`, the lock file that is used to produce the bundle fixes 
  an exact version ensuring that subsequent runs will always download the same 
  release.
- **Download hash pining**
  We apply a trust-on-first-download mode for all files, such that any 
  change in file hash for the same version can only be rectified through manual 
  intervention. This pinning also ensures a consistent input into the 
  customization stages
- **Useful tweaks**
  Remove modules that serve no purpose under your intended release scheme such 
  as the marketplace.
- **Tidy bundle**
  Bundles can optionally have packaging information(think `package.json` and 
  `.composer.lock`), example plugins and other supporting file removed to 
  keep the bundle size down.
- **Safe & shareable caching**
  Source zip files are cached locally for faster subsequent builds. Caches can 
  be shared across distributions, and each file has it's integrity checked 
  against the expected hashes stored in the distribution's lock file.
