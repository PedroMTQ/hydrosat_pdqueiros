from dataclasses import dataclass, field

import numpy as np

from hydrosat_pdqueiros.services.io.logger import logger


@dataclass
class BaseDocument():
    coordinatesXMin: float = field(repr=False)
    coordinatesYMin: float = field(repr=False)
    coordinatesXMax: float = field(repr=False)
    coordinatesYMax: float = field(repr=False)
    boxId : str
    irrigationgArray: np.array = field(default=None)
    isProcessed: np.array = field(default=False)

    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data.get('irrigationgArray'), list):
            data['irrigationgArray'] = np.array(data['irrigationgArray'])
        try:
            return cls(**data)
        except Exception as e:
            logger.exception(e)
            return None


    # fake processing
    def process(self):
        self.isProcessed = True

    def to_dict(self):
        return {
                'boxId': self.boxId,
                'coordinatesXMin': self.coordinatesXMin,
                'coordinatesYMin': self.coordinatesYMin,
                'coordinatesXMax': self.coordinatesXMax,
                'coordinatesYMax': self.coordinatesYMax,
                'irrigationgArray': self.irrigationgArray.tolist(),
                'isProcessed': self.isProcessed,
        }

if __name__ == '__main__':
    base_doc = BaseDocument(0,0,2,2,3)
