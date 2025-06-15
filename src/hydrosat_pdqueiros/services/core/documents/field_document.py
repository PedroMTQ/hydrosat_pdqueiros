from dataclasses import dataclass

import numpy as np
from shapely.geometry import box

from hydrosat_pdqueiros.services.core.documents import BaseDocument, BoundingBoxDocument


@dataclass
class FieldDocument(BaseDocument):

    def __post_init__(self):
        if self.irrigationgArray is None:
            height = self.coordinatesYMax - self.coordinatesYMin
            width = self.coordinatesXMax - self.coordinatesXMin
            self.irrigationgArray = np.zeros((height, width))

    def is_valid(self) -> bool:
        return self.irrigationgArray.all()

    def irrigate(self, bounding_box_document: BoundingBoxDocument):
        bounding_box = box(minx=bounding_box_document.coordinatesXMin,
                           miny=bounding_box_document.coordinatesYMin,
                           maxx=bounding_box_document.coordinatesXMax,
                           maxy=bounding_box_document.coordinatesYMax,
                            )
        field_box = box(minx=self.coordinatesXMin,
                        miny=self.coordinatesYMin,
                        maxx=self.coordinatesXMax,
                        maxy=self.coordinatesYMax,
                         )
        if not bounding_box.intersects(field_box):
            return
        # non-sensical but does the job for now
        height = int(self.coordinatesXMax- self.coordinatesYMin)
        width = int(self.coordinatesXMax - self.coordinatesXMin)
        self.irrigationgArray = np.random.choice([0, 1], size=(height, width))


if __name__ == '__main__':
    field_1 = FieldDocument(0,0,2,2,2)
    bounding_box = BoundingBoxDocument(0,0,5,5, 1)
    print(field_1)
    print(field_1.irrigationgArray)
    print(field_1.irrigationgArray.any())
    print(field_1.irrigate(bounding_box))
    print(field_1.irrigationgArray)
    print(field_1.irrigationgArray.any())
