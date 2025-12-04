<img src="https://avatars3.githubusercontent.com/u/29313215?v=3&s=200" align="right">

# Pirates of the Caribbean Online Rewritten

Pirates of the Caribbean Online Rewritten is a custom private server for Disney's defunct MMORPG; Pirates of the Caribbean online. Built using the 2013 client code, latest Panda3D and the Astron server

## Local setup (what you need installed)

- Python 2.7 with a Panda3D 1.9.x runtime that provides the `ppython` launcher (the scripts call `ppython`). Ensure `ppython` is on PATH and `PYTHONPATH` includes the Panda `python` folder (e.g., `.../built_x64/python`).
- Python packages in that same environment: `ppython -m pip install requests pywin32` (plus any others you need).
- Panda3D asset packs are **not** in the repo. Clone/download `PiratesOnlineRewritten/Resources` into a sibling folder named `resources` (paths like `../resources/phase_3`, `../resources/phase_4` must exist to satisfy the `model-path` entries in `config/general.prc`).
- Astron cluster binaries are not vendored. Drop your platform build into `astron/win32/astrond.exe`, `astron/linux/astrondlinux`, or `astron/darwin/astrond` as appropriate (the startup scripts expect those names).

## Running the stack (Windows)

Run each item in its own terminal from the repo root (`C:\Users\...\POTCO\Pirates-Online-Rewritten`):

1) Astron: `astron\win32\start_astron.bat` (accept default `astrond.yml`). Keep only one instance to avoid port bind errors.
2) UberDOG: `astron\win32\start_uberdog.bat` (loops to keep UD alive).
3) AI shard: `astron\win32\start_ai.bat` (defaults are fine). It will log warnings about missing island/boss data because those assets are absent in the public pack; they’re expected and harmless.
4) Client: `win32\start_client.bat` → choose “Localhost” and token `dev` to connect to your local shard. The script uses `ppython`; if your launcher name differs, set `PYTHON_CMD` inside the bat file.


Or run the startup script which runs all of the steps above. .\win32\start_stack.bat

Config touchpoints:
- Client/game flags: `config/general.prc` (+ `config/dev.prc`).
- Server flags (e.g., webhook URL): `config/server.prc`.
- Astron cluster layout: `astron/config/astrond.yml`.

## License

PiratesOnlineRewritten is licensed under the "BSD 3-Clause" for more info, refer to the [LICENSE](LICENSE) file.
