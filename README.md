<img src="https://avatars3.githubusercontent.com/u/29313215?v=3&s=200" align="right">

# Pirates of the Caribbean Online Rewritten

Pirates of the Caribbean Online Rewritten is a custom private server for Disney's defunct MMORPG; Pirates of the Caribbean online. Built using the 2013 client code, latest Panda3D and the Astron server

## Local setup (what you need installed)

- Python 2.7 with the Panda3D runtime that provides the `ppython` launcher (the shipped scripts call `ppython`; Panda3D 1.9.x builds ship it by default).
- Panda3D asset packs are **not** in the repo. Place the game resource phases in a sibling folder to this repo (paths like `../resources/phase_3`, `../resources/phase_4`, etc. relative to the repo root, matching the `model-path` entries in `config/general.prc`).
- Astron cluster binaries are not vendored. Drop your platform build into `astron/win32/astrond.exe`, `astron/linux/astrondlinux`, or `astron/darwin/astrond` as appropriate (the startup scripts expect those names).
- Python packages: install `requests` (webhooks/analytics) and `pywin32` (Windows launcher support) into the same Python/Panda3D environment: `ppython -m pip install requests pywin32`.

## Running the stack

Windows quick-start (run each in its own terminal, repo root unless noted):
1) Astron: `astron\\win32\\start_astron.bat` (defaults to `astron/config/astrond.yml` and writes to `astron/databases/astrondb`).
2) UberDOG: `astron\\win32\\start_uberdog.bat` (starts `pirates.uberdog.ServiceStart`).
3) AI shard: `astron\\win32\\start_ai.bat` (accept defaults for district/base channel or override when prompted).
4) Client: `win32\\start_client.bat` (select gameserver, token defaults to `dev`). The script calls `ppython -m pirates.piratesbase.PiratesStart`; if `ppython` is not on PATH, set `PYTHON_CMD` in the script to your Python 2.7 path.

Notes and configs:
- Client Panda3D/game flags: `config/general.prc` (+ `config/dev.prc`).
- Server flags (e.g., webhook URL): `config/server.prc`.
- Astron cluster layout: `astron/config/astrond.yml`.

## License

PiratesOnlineRewritten is licensed under the "BSD 3-Clause" for more info, refer to the [LICENSE](LICENSE) file.
