from panda3d.core import ConfigVariableString, ConfigVariableBool
import string
import types

# Read language from config vars; avoid simbase dependency.
language = ConfigVariableString('language', 'english').getValue()
checkLanguage = ConfigVariableBool('check-language', False).getValue()

def getLanguage():
    return language

print 'OTPLocalizer: Running in language: %s' % language
if language == 'english':
    _languageModule = 'otp.otpbase.OTPLocalizer' + string.capitalize(language)
else:
    checkLanguage = 1
    _languageModule = 'otp.otpbase.OTPLocalizer_' + language

print 'from ' + _languageModule + ' import *'
exec 'from ' + _languageModule + ' import *'
if checkLanguage:
    l = {}
    g = {}
    englishModule = __import__('otp.otpbase.OTPLocalizerEnglish', g, l)
    foreignModule = __import__(_languageModule, g, l)
    for key, val in englishModule.__dict__.items():
        if not foreignModule.__dict__.has_key(key):
            print 'WARNING: Foreign module: %s missing key: %s' % (_languageModule, key)
            locals()[key] = val
        elif isinstance(val, types.DictType):
            fval = foreignModule.__dict__.get(key)
            for dkey, dval in val.items():
                if not fval.has_key(dkey):
                    print 'WARNING: Foreign module: %s missing key: %s.%s' % (_languageModule, key, dkey)
                    fval[dkey] = dval

            for dkey in fval.keys():
                if not val.has_key(dkey):
                    print 'WARNING: Foreign module: %s extra key: %s.%s' % (_languageModule, key, dkey)

    for key in foreignModule.__dict__.keys():
        if not englishModule.__dict__.has_key(key):
            print 'WARNING: Foreign module: %s extra key: %s' % (_languageModule, key)
