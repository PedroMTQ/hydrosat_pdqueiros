from dataclasses import dataclass

import numpy as np

from hydrosat_pdqueiros.services.core.documents.base_document import BaseDocument


@dataclass
class BoundingBoxDocument(BaseDocument):
    def __post_init__(self):
        if self.irrigationgArray is None:
            height = int(self.coordinatesYMax - self.coordinatesYMin)
            width = int(self.coordinatesXMax - self.coordinatesXMin)
            self.irrigationgArray = np.random.choice([0, 1], size=(height, width))
        height = int(self.coordinatesYMax - self.coordinatesYMin)
        width = int(self.coordinatesXMax - self.coordinatesXMin)
        assert self.irrigationgArray.shape == (height, width), f'Array shape {self.irrigationgArray.shape} does not match expected ({height}, {width}) from coordinates'


    def is_valid(self) -> bool:
        return True



if __name__ == '__main__':
    doc = BoundingBoxDocument(coordinatesXMin=0,
                              coordinatesYMin=10,
                              coordinatesXMax=10,
                              coordinatesYMax=20,
                              boxId='hg',
                              )
    print(doc)
    doc_dict = doc.to_dict()
    print(doc_dict)
    doc = BoundingBoxDocument.from_dict(doc_dict)
    print('2', doc)
