from __future__ import division, print_function
from .base_model import BaseModel


class FabryPerotModel(BaseModel):

    def __init__(self):
        super(FabryPerotModel, self).__init__()
        self.image_name = None
        self.background_name = None
        self.super_pixel = None
        self.pixel_size = None
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

