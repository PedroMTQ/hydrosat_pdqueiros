import os

from dagster import OpExecutionContext, Output, asset

from hydrosat_pdqueiros.defs.partitions import DAILY_PARTITIONS
from hydrosat_pdqueiros.services.core.documents.asset_data_document import AssetDataDocument
from hydrosat_pdqueiros.services.core.documents.bounding_box_document import BoundingBoxDocument
from hydrosat_pdqueiros.services.core.documents.field_document import FieldDocument
from hydrosat_pdqueiros.services.settings import (
    BOXES_FOLDER_INPUT,
    BOXES_FOLDER_OUTPUT,
    FIELDS_FOLDER_INPUT,
    FIELDS_FOLDER_OUTPUT,
    TEMP,
)


@asset(
    partitions_def=DAILY_PARTITIONS,
    io_manager_key="io_manager_fields",
    required_resource_keys={'s3_resource'},
    kinds=['s3'],
    description='Downloads, processes, and uploads fields data from and to S3'
)
def asset_fields(context: OpExecutionContext):
    '''
    reads field data, processes it and sends it to the next asset (s3 field data uploader)
    '''
    partition_date = context.partition_key
    box_id = context.run_tags.get('box_id')
    asset_data_document = AssetDataDocument(s3_path=context.run_tags.get('s3_path'),
                                            local_input_folder_path=os.path.join(TEMP, FIELDS_FOLDER_INPUT, box_id),
                                            local_output_folder_path=os.path.join(TEMP, FIELDS_FOLDER_OUTPUT, box_id),
                                            document_type=FieldDocument.__name__)
    s3_output_path = os.path.join(FIELDS_FOLDER_OUTPUT, box_id, asset_data_document.file_name)
    context.log.info(f'Processing input s3 data for {partition_date} from {asset_data_document.s3_path}')
    return Output({'local_input_file_path': asset_data_document.local_input_file_path,
                   'local_output_file_path': asset_data_document.local_output_file_path,
                   's3_path': asset_data_document.s3_path,
                   'document_type': asset_data_document.document_type,
                   's3_output_path': s3_output_path,
                   },
                    metadata={
                        'box_id': box_id,
                        'partition_date': partition_date,
                        'document_type': asset_data_document.document_type})

@asset(
    io_manager_key="io_manager_bounding_box",
    required_resource_keys={'s3_resource'},
    kinds=['s3'],
    description='Downloads and processes boxes data from S3'
)
def asset_bounding_box(context: OpExecutionContext):
    '''
    reads bounding box data, processes it and sends it to the next asset (s3 bounding box data uploader)
    '''
    asset_data_document = AssetDataDocument(s3_path=context.run_tags.get('s3_path'),
                                            local_input_folder_path=os.path.join(TEMP, BOXES_FOLDER_INPUT),
                                            local_output_folder_path=os.path.join(TEMP, BOXES_FOLDER_OUTPUT),
                                            document_type=BoundingBoxDocument.__name__)
    s3_output_path = os.path.join(BOXES_FOLDER_OUTPUT, asset_data_document.file_name)
    context.log.info(f'Processing input s3 data from {asset_data_document.s3_path}')
    return Output({'local_input_file_path': asset_data_document.local_input_file_path,
                   'local_output_file_path': asset_data_document.local_output_file_path,
                   's3_path': asset_data_document.s3_path,
                   'document_type': asset_data_document.document_type,
                   's3_output_path': s3_output_path,
                   },
                    metadata={'document_type': asset_data_document.document_type})
