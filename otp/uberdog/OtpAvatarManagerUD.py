from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify import DirectNotifyGlobal

class OtpAvatarManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('OtpAvatarManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)

    def requestRemoveAvatar(self, context, avId, subId, confirmPassword):
        """
        Forward avatar deletion to the ClientServicesManager and respond
        immediately so the client UI can unblock.
        """
        self.notify.info('requestRemoveAvatar: avId=%s subId=%s context=%s sender=%s' %
                         (avId, subId, context, self.air.getMsgSender()))
        accountId = self.air.getAccountIdFromSender()
        if not accountId:
            self.notify.warning('requestRemoveAvatar with no account bound; rejecting.')
            self.sendUpdateToChannel(self.air.getMsgSender(), 'rejectRemoveAvatar', [0])
            return

        # Kick off the actual delete using the CSM flow (handles DB updates).
        if hasattr(self.air, 'csm') and self.air.csm:
            self.air.csm.deleteAvatar(avId)
        else:
            self.notify.warning('CSM missing; cannot perform avatar delete for %s' % avId)

        # Let the client proceed; it will pull a fresh avatar list afterwards.
        accountChannel = self.air.csm.GetAccountConnectionChannel(accountId) if hasattr(self.air, 'csm') else (accountId << 32)
        sender = self.air.getMsgSender()
        # Send to both the account channel and the direct sender to be safe.
        self.sendUpdateToChannel(accountChannel, 'removeAvatarResponse', [avId, subId])
        if sender != accountChannel:
            self.sendUpdateToChannel(sender, 'removeAvatarResponse', [avId, subId])
