Changes
-------


kdb 1.0.2.dev
.............

- Fixed a typo in Greeting Plugin


kdb 1.0.1 (*2014-04-16*)
........................

- Fixed Web Plugin proper and make package non ``zip_safe``.
- Fixed templates path in Web Plugin.
- Fixed the Web Plugin so it works if installed as a package and run
  separately.


kdb 1.0.0 (*2014-04-16*)
........................

- Fixed missing ``html2text`` and ``aspell-en`` dependency.
- Updated requirements and Dockerfile
- Moved example config into ``etc/``
- Print a treceback on plugin load failure.
- Use ``os.path.exists`` to check for ``--config`` file.
- Fixed Dockerfile
- Added Remote Plugin Plugin
- Fixed sub-commands for Channels Plugin.
- Fixed state management.
- Set a filename to save RSS Feeds to for the RSS Plugin in the default
  sample configuration file.
- Fixed sub-commands with the Channels Plugin.
- Fixed display of ``RLIST`` command in RSS Plugin.
- Fixed counting usage statistics of commands.


kdb 0.9.0 (*2014-04-14*)
........................

- Ported to circuits 3.0
