from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify import DirectNotifyGlobal
from otp.distributed.OtpDoGlobals import OTP_ZONE_ID_MANAGEMENT
from pirates.uberdog.UberDogGlobals import InventoryId, InventoryType
from pirates.uberdog import InventoryInit

def _get_inv_dclass(air):
    # Prefer the canonical dc name (PirateInventory), fall back to AI/UD variants.
    return (air.dclassesByName.get('PirateInventory')
            or air.dclassesByName.get('PirateInventoryAI')
            or air.dclassesByName.get('PirateInventoryUD'))

class DistributedInventoryManagerAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedInventoryManagerAI')

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)

        self.inventories = {}
        self.pendingSend = {}

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
        self.notify.warning('InventoryManagerAI generated with doId %s' % self.doId)

    def hasInventory(self, inventoryId):
        return inventoryId in self.inventories

    def addInventory(self, inventory):
        if self.hasInventory(inventory.doId):
            return self.notify.warning('Tried to add an already existing inventory %d!' % inventory.doId)

        self.inventories[inventory.doId] = inventory
        self.notify.warning('Inventory %d registered for owner %d' % (inventory.doId, inventory.getOwnerId()))

        # If anyone was waiting on this inventory to load, fulfill now.
        waiting = self.pendingSend.pop(inventory.doId, [])
        for avId in waiting:
            avatar = self.air.doId2do.get(avId)
            if avatar:
                self.notify.warning('Inventory %d loaded; delivering to avatar %d' % (inventory.doId, avId))
                self.__sendInventory(avatar, inventory)

    def removeInventory(self, inventory):
        if not self.hasInventory(inventory.doId):
            return self.notify.warning('Tried to remove a non-existant inventory %d!' % inventory.doId)

        del self.inventories[inventory.doId]

    def getInventory(self, avatarId):
        for inventory in self.inventories.values():
            if inventory.getOwnerId() == avatarId:
                return inventory
        return None

    def requestInventory(self):
        senderId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(senderId)

        if not avatar:
            self.notify.warning('AI requestInventory received from sender %s but no avatar found in doId2do' % senderId)
            return

        self.notify.warning('AI requestInventory from avatar %s (sender %s)' % (avatar.doId, senderId))
        def queryAvatar(dclass, fields):
            if not dclass or not fields:
                return self.notify.warning('Failed to query avatar %d!' % avatar.doId)

            inventoryId, = fields.get('setInventoryId', (0,))

            if not inventoryId:
                self.notify.warning('No inventoryId for avatar %d; creating one' % avatar.doId)
                return self.__createInventory(avatar)

            self.notify.warning('Avatar %d has inventoryId %d' % (avatar.doId, inventoryId))
            self.__sendInventory(avatar, self.inventories.get(inventoryId), inventoryId)

        self.air.dbInterface.queryObject(self.air.dbId, avatar.doId, callback=queryAvatar,
            dclass=self.air.dclassesByName['DistributedPlayerPirateAI'])

    def __sendInventory(self, avatar, inventory, inventoryId=None):
        invId = inventory.doId if inventory else inventoryId
        if not invId:
            return self.notify.warning('No inventory id available for avatar %d' % avatar.doId)

        if not inventory:
            # Not loaded yet; request activation and queue the send.
            pending = self.pendingSend.setdefault(invId, [])
            if avatar.doId not in pending:
                pending.append(avatar.doId)
                invDclass = _get_inv_dclass(self.air)
                if not invDclass:
                    return self.notify.warning('No inventory dclass available to activate %d' % invId)
                self.notify.warning('Inventory %d not loaded; activating for avatar %d using dclass %s'
                                    % (invId, avatar.doId, invDclass.getName()))
                self.notify.warning('Pending queue for inventory %d now: %s' % (invId, pending))
                self.air.sendActivate(invId, avatar.doId, OTP_ZONE_ID_MANAGEMENT, dclass=invDclass)

            return

        inventory.b_setStackLimit(InventoryType.Hp, avatar.getMaxHp())
        inventory.b_setStackLimit(InventoryType.Mojo, avatar.getMaxMojo())

        for index in xrange(len(inventory.accumulators)):
            inventory.d_setAccumulator(*inventory.accumulators[index])

        for index in xrange(len(inventory.stackLimits)):
            inventory.d_setStackLimit(*inventory.stackLimits[index])

        for index in xrange(len(inventory.stacks)):
            inventory.d_setStack(*inventory.stacks[index])

        inventory.d_requestInventoryComplete()
        self.notify.warning('Delivered inventory %d to avatar %d' % (inventory.doId, avatar.doId))

    def __createInventory(self, avatar):
        """
        Create a fresh inventory record and attach to the avatar.
        """
        accumulators = [[InventoryType.OverallRep, 0]]
        categoryLimits = [(k, v) for k, v in InventoryInit.CategoryLimits.iteritems()]
        stackLimits = [(k, v) for k, v in InventoryInit.StackLimits.iteritems()]
        startStacks = [(k, v) for k, v in InventoryInit.StackStartsWith.iteritems()]

        def inventoryCreated(inventoryId):
            if not inventoryId:
                return self.notify.warning('Failed to create inventory for %d!' % avatar.doId)

            def inventorySet(fields):
                if fields:
                    return self.notify.warning('Failed to set inventory %d for %d!' % (inventoryId, avatar.doId))
                self.notify.warning('Created inventory %d for avatar %d' % (inventoryId, avatar.doId))
                # Activate and deliver
                invDclass = _get_inv_dclass(self.air)
                if not invDclass:
                    return self.notify.warning('No inventory dclass available to activate %d' % inventoryId)
                self.air.sendActivate(inventoryId, avatar.doId, OTP_ZONE_ID_MANAGEMENT, dclass=invDclass)
                self.pendingSend.setdefault(inventoryId, []).append(avatar.doId)

            self.air.dbInterface.updateObject(self.air.dbId, avatar.doId,
                self.air.dclassesByName['DistributedPlayerPirateAI'],
                {'setInventoryId': (inventoryId,)}, callback=inventorySet)

        invDclass = _get_inv_dclass(self.air)
        if not invDclass:
            return self.notify.warning('No inventory dclass available to create for avatar %d' % avatar.doId)
        self.air.dbInterface.createObject(self.air.dbId, invDclass,
            fields={
                'setOwnerId': (avatar.doId,),
                'setInventoryVersion': (InventoryInit.UberDogRevision,),
                'setCategoryLimits': (categoryLimits,),
                'setAccumulators': (accumulators,),
                'setStackLimits': (stackLimits,),
                'setStacks': (startStacks,)
            }, callback=inventoryCreated)
