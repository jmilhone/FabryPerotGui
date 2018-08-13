import collections


class FabryPerotModel(object):

    def __init__(self):
        super(FabryPerotModel, self).__init__()
        self.image_name = None
        self.background_name = None
        self.super_pixel = None
        self.binsize = None
        self.image = None
        self.background = None
        self.r = None
        self.ringsum = None
        self.ringsum_err = None
        self.center = None
        self.center = None #(2992, 1911)

        self.status = 'Idle'
        self.update_registry = {'image_data': list(),
                                'ringsum_data': list(),
                                'status': list(),
                                }

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

    def to_dict(self):
        """

        :return:
        """
        output_dict = {'fname': self.image_name,
                       'bg_fname': self.background_name,
                       'center': self.center,
                       'r': self.r,
                       'sig': self.ringsum,
                       'sig_sd': self.ringsum_err
                       }
        return output_dict

