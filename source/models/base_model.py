import collections


class BaseModel(object):

    def __init__(self):
        super(BaseModel, self).__init__()
        self.update_registry = dict()

    def subscribe_update_func(self, fn, registry='data'):
        """Subscribe fn to be called when there is an update to registry

        :param fn: Function to to suscribe for update
        :type fn: collections.Callable
        :param registry: function is registered for updates to this event
        :type registry: str
        """
        current_registry = self.update_registry[registry]
        if fn not in current_registry:
            current_registry.append(fn)

    def unsubscribe_update_func(self, fn, registry='data'):
        """Unsubscribe fn to be called when there is an update to registry

        :param fn: Function to to suscribe for update
        :type fn: collections.Callable
        :param registry: function is registered for updates to this event
        :type registry: str
        """
        current_registry = self.update_registry[registry]
        if fn in current_registry:
            current_registry.remove(fn)

    def announce_update(self, registry='data'):
        """Call all functions in registry for updates

        :param registry: registry that has been updated
        :type registry: str
        """
        current_registry = self.update_registry[registry]
        for fn in current_registry:
            fn()



