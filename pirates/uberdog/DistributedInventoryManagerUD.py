from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify import DirectNotifyGlobal
from direct.fsm.FSM import FSM
from otp.distributed.OtpDoGlobals import *
from pirates.uberdog import InventoryInit
from pirates.uberdog.UberDogGlobals import InventoryId, InventoryType

def _get_inv_dclass(air):
    # Prefer the canonical dc name (PirateInventory), fall back to AI/UD variants.
    return (air.dclassesByName.get('PirateInventory')
            or air.dclassesByName.get('PirateInventoryAI')
            or air.dclassesByName.get('PirateInventoryUD'))

class InventoryFSM(FSM):

    def __init__(self, manager, avatarId, callback):
        self.manager = manager
        self.avatarId = avatarId
        self.callback = callback

        FSM.__init__(self, 'InventoryFSM')

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterStart(self):

        def queryAvatar(dclass, fields):
            if not dclass or not fields:
                return self.notify.warning('Failed to query avatar %d!' % self.avatarId)

            inventoryId, = fields.get('setInventoryId', (0,))

            if not inventoryId:
                self.request('Create')
            else:
                self.request('Load', inventoryId)

        self.manager.air.dbInterface.queryObject(self.manager.air.dbId, self.avatarId, queryAvatar,
            dclass=self.manager.air.dclassesByName['DistributedPlayerPirateUD'])

    def exitStart(self):
        pass

    def enterCreate(self):
        invDclass = _get_inv_dclass(self.manager.air)
        if not invDclass:
            return self.notify.error('No inventory dclass available to create for avatar %s' % self.avatarId)
        self.notify.warning('Creating inventory object for avatar %s using dclass %s' % (self.avatarId, invDclass.getName()))

        def inventorySet(fields, inventoryId):
            if fields:
                return self.notify.warning('Failed to set inventory %d for %d!' % (inventoryId, self.avatarId))

            # Activate the inventory so the client can pull it immediately.
            invDclass = _get_inv_dclass(self.manager.air)
            if not invDclass:
                return self.notify.error('No inventory dclass available to activate %d' % inventoryId)
            self.notify.warning('Activating new inventory %s for avatar %s' % (inventoryId, self.avatarId))
            self.manager.air.sendActivate(inventoryId, self.avatarId, OTP_ZONE_ID_MANAGEMENT, dclass=invDclass)

            del self.manager.avatar2fsm[self.avatarId]
            self.demand('Off')
            self.callback(inventoryId)

        def inventoryCreated(inventoryId):
            if not inventoryId:
                return self.notify.warning('Failed to create inventory for %d!' % self.avatarId)

            self.manager.air.dbInterface.updateObject(self.manager.air.dbId, self.avatarId, self.manager.air.dclassesByName['DistributedPlayerPirateUD'],
                {'setInventoryId': (inventoryId,)}, callback=lambda fields: inventorySet(fields, inventoryId))

        accumulators = []
        accumulators.append([InventoryType.OverallRep, 0])

        categoryLimits = []
        for key, limit in InventoryInit.CategoryLimits.iteritems():
            categoryLimits.append((key, limit))

        stackLimits = []
        for key, limit in InventoryInit.StackLimits.iteritems():
            stackLimits.append((key, limit))

        startStacks = []
        for key, amount in InventoryInit.StackStartsWith.iteritems():
            startStacks.append((key, amount))

        # Create using the available inventory dclass (AI preferred).
        self.manager.air.dbInterface.createObject(self.manager.air.dbId, invDclass,
            fields={
                'setOwnerId': (self.avatarId,),
                'setInventoryVersion': (InventoryInit.UberDogRevision,),
                'setCategoryLimits': (categoryLimits,),
                'setAccumulators': (accumulators,),
                'setStackLimits': (stackLimits,),
                'setStacks': (startStacks,)
            }, callback=inventoryCreated)

    def exitCreate(self):
        pass

    def enterLoad(self, inventoryId):
        if not inventoryId:
            return self.warning('Failed to activate invalid inventory object!')

        invDclass = _get_inv_dclass(self.manager.air)
        if not invDclass:
            return self.notify.error('No inventory dclass available to load for avatar %s' % self.avatarId)

        def afterQuery(dclass, fields):
            if not dclass or not fields:
                self.notify.warning('Inventory %s missing in DB; recreating for avatar %s' % (inventoryId, self.avatarId))
                return self.request('Create')

            if dclass.getName() != invDclass.getName():
                self.notify.warning('Inventory %s dclass %s mismatch (expected %s); recreating for avatar %s'
                                    % (inventoryId, dclass.getName(), invDclass.getName(), self.avatarId))
                return self.request('Create')

            self.notify.warning('Inventory %s found in DB with dclass %s' % (inventoryId, dclass.getName()))
            self.notify.warning('Activating inventory %s for avatar %s using dclass %s'
                                % (inventoryId, self.avatarId, invDclass.getName()))
            self.manager.air.sendActivate(inventoryId, self.avatarId, OTP_ZONE_ID_MANAGEMENT, dclass=invDclass)

            del self.manager.avatar2fsm[self.avatarId]
            self.demand('Off')
            self.callback(inventoryId)

        # Verify the inventory object exists before we try to activate it
        # Query as the AI-side class; if missing, we'll recreate.
        self.manager.air.dbInterface.queryObject(self.manager.air.dbId, inventoryId, afterQuery,
                                                 dclass=invDclass)

    def exitLoad(self):
        pass

class DistributedInventoryManagerUD(DistributedObjectGlobalUD):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedInventoryManagerUD')

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)

        self.avatar2fsm = {}
        # doId is assigned after generation; avoid touching it here
        self.notify.warning('InventoryManagerUD init (doId not assigned yet)')

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        self.notify.warning('InventoryManagerUD generated with doId %s' % self.doId)

    def initiateInventory(self, avatarId, callback):
        if not avatarId:
            return self.notify.warning('Failed to initiate inventory for invalid avatar!')

        if not callable(callback):
            self.notify.error('Failed to initiate inventory, callback not callable!')

        if avatarId in self.avatar2fsm:
            return self.notify.warning('Failed to initiate inventory for already existing avatar %s!' % avatarId)

        self.notify.warning('Initiating inventory request for avatar %s' % avatarId)
        self.avatar2fsm[avatarId] = InventoryFSM(self, avatarId, callback)
        self.avatar2fsm[avatarId].request('Start')
