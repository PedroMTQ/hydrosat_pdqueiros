from dagster import Definitions

from hydrosat_pdqueiros.defs.assets import (
    asset_bounding_box,
    asset_fields,
)
from hydrosat_pdqueiros.defs.io_managers import (
    io_manager_bounding_box,
    io_manager_fields,
)
from hydrosat_pdqueiros.defs.jobs import job_process_bounding_boxes, job_process_fields
from hydrosat_pdqueiros.defs.resources import s3_resource
from hydrosat_pdqueiros.defs.sensors import sensor_bounding_boxes, sensor_fields

defs = Definitions(
    assets=[asset_bounding_box, asset_fields],
    jobs=[job_process_fields, job_process_bounding_boxes],
    sensors=[sensor_fields, sensor_bounding_boxes],
    resources={
        "s3_resource": s3_resource,
        "io_manager_fields": io_manager_fields,
        "io_manager_bounding_box": io_manager_bounding_box,
    },
)
