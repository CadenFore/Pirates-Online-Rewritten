import sys
import traceback

from direct.directnotify.DirectNotifyGlobal import directNotify
from pirates.distributed.PiratesInternalRepository import PiratesInternalRepository
from direct.distributed.PyDatagram import *
from otp.distributed.DistributedDirectoryAI import DistributedDirectoryAI
from otp.distributed.OtpDoGlobals import *
from pirates.uberdog.PiratesRPCServerUD import PiratesRPCServerUD
from pirates.uberdog.DistributedInventoryManagerUD import DistributedInventoryManagerUD

class PiratesUberRepository(PiratesInternalRepository):
    notify = directNotify.newCategory('PiratesUberRepository')
    notify.setInfo(True)

    def __init__(self, baseChannel, serverId):
        PiratesInternalRepository.__init__(self, baseChannel, serverId, dcSuffix='UD')
        self.rpc = None
        self.districtTracker = None

    def handleConnected(self):
        rootObj = DistributedDirectoryAI(self)
        rootObj.generateWithRequiredAndId(self.getGameDoId(), 0, 0)

        if config.GetBool('want-rpc-server', True):
            self.rpc = PiratesRPCServerUD(self)
            self.rpc.daemon = True
            self.rpc.start()

        self.createGlobals()
        self.notify.info('UberDOG ready!')

    def createGlobals(self):
        """
        Create "global" objects.
        """
        try:
            # Explicit prints so we can see generation progress even when logging is buffered.
            print '[UD] Generating globals...'; sys.stdout.flush()
            self.notify.warning('Generating globals...')
            self.centralLogger = self.generateGlobalObject(OTP_DO_ID_CENTRAL_LOGGER, 'CentralLogger')
            self.csm = self.generateGlobalObject(OTP_DO_ID_CLIENT_SERVICES_MANAGER, 'ClientServicesManager')
            self.travelAgent = self.generateGlobalObject(OTP_DO_ID_PIRATES_TRAVEL_AGENT, 'DistributedTravelAgent')
            # Avatar manager (handles delete/create requests and avatar lists).
            self.notify.warning('Generating AvatarManager (DOID %s)...' % OTP_DO_ID_PIRATES_AVATAR_MANAGER)
            self.avatarManager = self.generateGlobalObject(OTP_DO_ID_PIRATES_AVATAR_MANAGER, 'DistributedAvatarManager')
            self.notify.warning('AvatarManager generated: %s' % bool(self.avatarManager))
            # Use a local (non-global) UD inventory manager so we avoid DOID conflicts with the AI-side
            # inventory manager, while still letting ClientServicesManager perform DB setup.
            if config.GetBool('want-ud-inventory-manager', False):
                # Legacy path: generate a full global object if explicitly requested.
                self.inventoryManager = self.generateGlobalObject(OTP_DO_ID_PIRATES_INVENTORY_MANAGER, 'DistributedInventoryManager')
            else:
                self.inventoryManager = DistributedInventoryManagerUD(self)
                self.notify.warning('Created local InventoryManagerUD helper (non-global) to service CSM login flow')
            self.holidayMgr = self.generateGlobalObject(OTP_DO_ID_PIRATES_HOLIDAY_MANAGER, 'HolidayManager')
            self.codeMgr = self.generateGlobalObject(OTP_DO_ID_PIRATES_CODE_REDEMPTION, 'CodeRedemption')
            self.chatManager = self.generateGlobalObject(OTP_DO_ID_CHAT_MANAGER, 'DistributedChatManager')
            self.speedChatRelay = self.generateGlobalObject(OTP_DO_ID_PIRATES_SPEEDCHAT_RELAY, 'PiratesSpeedchatRelay')
            self.crewMatchManager = self.generateGlobalObject(OTP_DO_ID_PIRATES_CREW_MATCH_MANAGER, 'DistributedCrewMatchManager')
            self.guildManager = self.generateGlobalObject(OTP_DO_ID_PIRATES_GUILD_MANAGER, 'PCGuildManager')
            self.friendsManager = self.generateGlobalObject(OTP_DO_ID_PIRATES_FRIENDS_MANAGER, 'PCAvatarFriendsManager')
            print '[UD] Globals ready.'; sys.stdout.flush()
            self.notify.warning('Global generation complete.')
        except Exception:
            print '[UD] Exception during globals:'
            traceback.print_exc()
            self.notify.warning('Failed to generate globals: %s' % traceback.format_exc())
            raise
