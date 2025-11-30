"""
Compatibility shim to restore POD/ParamObj helpers expected by POTCO code.
Newer Panda3D builds omit these legacy utilities.
"""

import direct.showbase.PythonUtil as PU


if not hasattr(PU, 'POD'):
    class POD(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __getattr__(self, name):
            if name.startswith('set') and len(name) > 3:
                attr = name[3:]
                attr = attr[0].lower() + attr[1:]

                def setter(value):
                    setattr(self, attr, value)

                return setter
            if name.startswith('get') and len(name) > 3:
                attr = name[3:]
                attr = attr[0].lower() + attr[1:]

                def getter():
                    return getattr(self, attr, None)

                return getter
            raise AttributeError(name)

    PU.POD = POD


if not hasattr(PU, 'ParamObj'):
    class ParamObj(object):
        class ParamSet(object):
            Params = {}

            def __init__(self, **kwargs):
                self.__dict__.update(self.Params)
                self.__dict__.update(kwargs)

        def __init__(self, *args, **kwargs):
            self._apply_defaults()
            if args and isinstance(args[0], dict) and not kwargs:
                for k, v in args[0].items():
                    setattr(self, k, v)
            else:
                for k, v in kwargs.items():
                    setattr(self, k, v)

        def _apply_defaults(self):
            ps = getattr(self, 'ParamSet', None)
            if ps and hasattr(ps, 'Params'):
                for k, v in ps.Params.items():
                    setattr(self, k, v)

        def getCurrentParams(self):
            ps = getattr(self, 'ParamSet', None)
            if ps and hasattr(ps, 'Params'):
                return {k: getattr(self, k, None) for k in ps.Params}
            return self.__dict__.copy()

        def __getattr__(self, name):
            # Auto-create simple setters (e.g., setFoo -> self.foo = value)
            if name.startswith('set') and len(name) > 3:
                attr = name[3:]
                attr = attr[0].lower() + attr[1:]

                def setter(value):
                    setattr(self, attr, value)

                return setter
            if name.startswith('get') and len(name) > 3:
                attr = name[3:]
                attr = attr[0].lower() + attr[1:]

                def getter():
                    return getattr(self, attr, None)

                return getter
            raise AttributeError(name)

    PU.ParamObj = ParamObj


if not hasattr(PU, 'getSetter'):
    def getSetter(name):
        def setter(self, value):
            setattr(self, name, value)

        return setter

    PU.getSetter = getSetter
