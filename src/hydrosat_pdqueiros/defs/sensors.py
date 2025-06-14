import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from dagster import (
    DefaultSensorStatus,
    RunRequest,
    SensorEvaluationContext,
    SkipReason,
    sensor,
)

from hydrosat_pdqueiros.defs.jobs import job_process_bounding_boxes, job_process_fields
from hydrosat_pdqueiros.defs.partitions import DAILY_PARTITIONS
from hydrosat_pdqueiros.services.io.logger import logger
from hydrosat_pdqueiros.services.io.run_logger import RunLogger
from hydrosat_pdqueiros.services.io.s3_client import ClientS3
from hydrosat_pdqueiros.services.settings import (
    BOXES_FOLDER_INPUT,
    BOXES_FOLDER_OUTPUT,
    BOXES_SENSOR_SLEEP_TIME,
    DATE_FORMAT,
    FIELDS_FOLDER_INPUT,
    FIELDS_FOLDER_OUTPUT,
    FIELDS_SENSOR_SLEEP_TIME,
    S3_BUCKET,
    S3_DATE_REGEX,
)

DATE_REGEX_PATTERN = re.compile(S3_DATE_REGEX)


# def yield_asset_materializations(context: SensorEvaluationContext, asset_key: AssetKey):
#     '''yields all records until where are no more results, i.e., event_record_has_more is False'''
#     cursor = None
#     while True:
#         result: EventRecordsResult = context.instance.fetch_materializations(records_filter=asset_key,
#                                                                              limit=MATERIALIZATIONS_FETCHER_LIMIT, cursor=cursor)
#         context.log.info(f'yielding: {asset_key}: {result}')

#         event_record: EventLogRecord
#         for event_record in result.records:
#             context.log.debug(f'event_record: {event_record}')
#             yield event_record
#         if not result.has_more:
#             return
#         cursor = result.cursor


# def has_event_record(context: SensorEvaluationContext,
#                      asset_key: AssetKey,
#                      s3_path: str) -> bool:
#     ''' iterates over all event records to find the one for a given run_id/s3_path'''
#     # this seems quite hacky, so maybe there's a better way?
#     # we could use AssetRecordsFilter for improved filtering (by date) but the date wouldn't necessarily match the one in the partition
#     event_record: EventLogRecord
#     for event_record in yield_asset_materializations(context=context,asset_key=asset_key):
#         event_tags = event_record.event_log_entry.dagster_event.logging_tags
#         context.log.info(f'event: {event_record} event_tags {event_tags}')
#         if event_record.run_id == s3_path:
#             return True
#     return False

# def has_event_record(s3_path: Optional[str]=None, pattern: Optional[re.Pattern]=None):
#     '''
#     this was meant to be used as a "DB" but it's not very robust, especially during testing. We will just check S3 instead.
#     '''
#     return RunLogger().run_finished(s3_path=s3_path, pattern=pattern)




def fields_dependencies_are_available(context: SensorEvaluationContext,
                                      s3_client: ClientS3,
                                      s3_path: str,
                                      box_id: str,
                                      date_str: str):
    '''checks if all dependencies for a field execution are met'''
    date_obj = datetime.strptime(date_str, DATE_FORMAT)
    all_dates = [datetime.strptime(partition_date, DATE_FORMAT) for partition_date in DAILY_PARTITIONS.get_partition_keys()]
    earliest_date = min(all_dates)
    # if this is the first asset, we need to assume there's no earlier dependencies
    if date_obj < earliest_date:
        context.log.info(f'Field data {s3_path} precedes the earliest partition date, skipping...')
        return False
    output_box_file = os.path.join(BOXES_FOLDER_OUTPUT, f'bounding_box_{box_id}.jsonl')
    if not s3_client.file_exists(output_box_file):
        context.log.info(f'Field data {s3_path} skipped since output box file {output_box_file} is not available yet')
        return False
    if date_obj == earliest_date:
        return True
    sorted_dates = sorted(all_dates)
    current_date_index = sorted_dates.index(date_obj)
    previous_date = sorted_dates[current_date_index-1]
    previous_date_str = previous_date.strftime(DATE_FORMAT)
    previous_date_s3_input_file_pattern = rf'fields\/input\/{box_id}\/fields_{previous_date_str}(.*)?\.jsonl$'
    previous_date_s3_output_file_pattern = rf'fields\/output\/{box_id}\/fields_{previous_date_str}(.*)?\.jsonl$'
    # we get the output files of the previous date
    previous_date_output_s3_files = set(s3_client.get_files(prefix=FIELDS_FOLDER_OUTPUT,
                                                            file_name_pattern=previous_date_s3_output_file_pattern,
                                                            match_on_s3_path=True))
    # if there are none we cannot run
    if not previous_date_output_s3_files:
        context.log.info(f'Field data {s3_path} depends on data from {previous_date_s3_output_file_pattern}, and the data was NOT found, skipping...')
        return False
    previous_date_input_s3_files = s3_client.get_files(prefix=FIELDS_FOLDER_INPUT,
                                                        file_name_pattern=previous_date_s3_input_file_pattern,
                                                        match_on_s3_path=True)
    # now if there are some but not the same as the input we also cannot run
    if len(previous_date_output_s3_files) != len(previous_date_input_s3_files):
        context.log.info(f'Field data {s3_path} depends on data from {previous_date_s3_output_file_pattern}, and only part of the data was found ({len(previous_date_output_s3_files)}/{len(previous_date_s3_input_file_pattern)}), skipping...')
        return False
    return True


@sensor(
    job=job_process_fields,
    # sets sensor to run automatically
    default_status=DefaultSensorStatus.RUNNING,
    required_resource_keys={"s3_resource"},
    minimum_interval_seconds=FIELDS_SENSOR_SLEEP_TIME,
)
def sensor_fields(context: SensorEvaluationContext):
    context.log.info("Running s3_check_sensor")
    s3_client: ClientS3 = context.resources.s3_resource
    s3_file_paths = []
    try:
        s3_file_paths = s3_client.get_input_fields()
    except Exception as e:
        context.log.exception(e)
        yield SkipReason(f"Error fetching S3 files: {e}")
        return
    if s3_file_paths is None:
        yield SkipReason(f'No file found in {os.path.join(S3_BUCKET, FIELDS_FOLDER_INPUT)}')
        return
    context.log.debug(f'Files in S3: {s3_file_paths}')
    run_requests = []
    for s3_path in s3_file_paths:
        # assuming this structure fields/input/01976a1225ca7e32a2daad543cb4391e/fields_2025-06-01.jsonl
        box_id = Path(Path(s3_path).parent).name
        date_str = DATE_REGEX_PATTERN.search(s3_path).group()
        if not fields_dependencies_are_available(context=context,
                                                 s3_client=s3_client,
                                                 s3_path=s3_path,
                                                 box_id=box_id,
                                                 date_str=date_str):
            continue
        if DAILY_PARTITIONS.has_partition_key(date_str):
            context.log.debug(f'Adding RunRequest for {s3_path}')
            run_requests.append(RunRequest(run_key=s3_path,
                                           partition_key=date_str,
                                           tags={"s3_path": s3_path,
                                                 'box_id': box_id,
                                                 'date_str': date_str,
                                                 },
                                           run_config={}
                                           ))
    if not run_requests:
        yield SkipReason('Skipping since fields data does not meet job dependencies')
    for run_request in run_requests:
        yield run_request


@sensor(
    job=job_process_bounding_boxes,
    # sets sensor to run automatically
    default_status=DefaultSensorStatus.RUNNING,
    required_resource_keys={"s3_resource"},
    minimum_interval_seconds=BOXES_SENSOR_SLEEP_TIME,
)
def sensor_bounding_boxes(context: SensorEvaluationContext):
    context.log.info("Running s3_check_sensor")
    s3_client: ClientS3 = context.resources.s3_resource
    try:
        s3_file_paths = s3_client.get_input_bounding_boxes()
    except Exception as e:
        yield SkipReason(f"Error fetching S3 files: {e}")
    if s3_file_paths is None:
        yield SkipReason(f'No file found in {os.path.join(S3_BUCKET, BOXES_FOLDER_INPUT)}')
    logger.info(f'Files in S3: {s3_file_paths}')
    run_requests = []
    for s3_path in s3_file_paths:
        box_id = Path(s3_path).stem.replace('bounding_box_', '')
        run_requests.append(RunRequest(run_key=s3_path,
                                       tags={"s3_path": s3_path,
                                             'box_id': box_id},
                                       run_config={}
                                       ))
    if not run_requests:
        yield SkipReason('Skipping since boxes files fall outside the required partitions')
    for run_request in run_requests:
        yield run_request
