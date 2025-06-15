from dagster import RetryPolicy, define_asset_job

from hydrosat_pdqueiros.defs.assets import (
    asset_bounding_box,
    asset_fields,
)
from hydrosat_pdqueiros.defs.partitions import DAILY_PARTITIONS
from hydrosat_pdqueiros.services.settings import RETRY_LIMIT

RETRY_POLICY = RetryPolicy(max_retries=RETRY_LIMIT)


job_process_fields = define_asset_job(name='job_process_fields',
                                      selection=[asset_fields],
                                      partitions_def=DAILY_PARTITIONS,
                                      op_retry_policy=RETRY_POLICY)

job_process_bounding_boxes = define_asset_job(name='job_process_bounding_boxes',
                                              selection=[asset_bounding_box],
                                              op_retry_policy=RETRY_POLICY)
