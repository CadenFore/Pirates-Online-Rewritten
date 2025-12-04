from direct.directnotify import DirectNotifyGlobal
from otp.uberdog.OtpAvatarManagerUD import OtpAvatarManagerUD

class DistributedAvatarManagerUD(OtpAvatarManagerUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedAvatarManagerUD')

    def __init__(self, air):
        OtpAvatarManagerUD.__init__(self, air)
