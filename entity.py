import copy


class EntityMeta(type):
    def __new__(mcs, clsname, superclasses, attributedict):
        clss = type.__new__(mcs, clsname, superclasses, attributedict)
        if 'cost' in attributedict:
            clss.message = "{} (${} monthly)".format(attributedict['formatted'], attributedict['cost'])
        else:
            clss.message = "{}".format(attributedict['formatted'])
        return clss


class Entity(object, metaclass=EntityMeta):
    current_amount = 0
    limit = -1
    unlocked = False
    unlocks_entities = []
    locks_entities = []
    cost = 0
    formatted = "Entity"
    drains = {}
    replenishes = {}
    inventory = {'money': 0}
    project = None

    def __init__(self, project=None, inventory=inventory, draining=drains, replenishing=replenishes):

        if self.__class__.limit >= 0:
            if self.__class__.current_amount >= self.__class__.limit:
                raise Entity.TooManyEntitiesException("No limit for {}".format(self.__class__.__name__))

        self.inventory = copy.deepcopy(inventory)
        self.draining = copy.deepcopy(draining)
        self.replenishing = copy.deepcopy(replenishing)
        self.project = project
        self.__class__.current_amount += 1
        self.__class__.unlocks()
        self.__class__.locks()

    def trade(self, to_entity, item, value):
        item1 = getattr(self, item)
        item2 = getattr(to_entity, item)
        setattr(self, item, item1-value)
        setattr(to_entity, item, item2+value)

    def turn(self):
        self.drain()
        self.replenish()

    def drain(self):
        for key, value in self.draining.items():
            self.inventory[key] -= value

    def replenish(self):
        for key, value in self.replenishing.items():
            self.inventory[key] += value

    @property
    def money(self):
        return self.inventory['money']

    @money.setter
    def money(self, value):
        self.inventory['money'] = value

    @classmethod
    def unlocks(cls):
        for entity in cls.unlocks_entities:
            entity.unlock()

    @classmethod
    def locks(cls):
        for entity in cls.locks_entities:
            entity.lock()

    @classmethod
    def unlock(cls):
        cls.unlocked = True

    @classmethod
    def lock(cls):
        cls.unlocked = False

    @classmethod
    def limit_reached(cls):
        if cls.limit >= 0:
            if cls.current_amount >= cls.limit:
                return True

        return False

    class TooManyEntitiesException(Exception):
        pass
