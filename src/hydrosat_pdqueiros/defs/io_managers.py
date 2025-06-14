import json
import os
from pathlib import Path
from abc import abstractmethod

from dagster import InputContext, IOManager, OutputContext, io_manager

from hydrosat_pdqueiros.services.core.documents.asset_data_document import AssetDataDocument
from hydrosat_pdqueiros.services.io.run_logger import RunLogger
from hydrosat_pdqueiros.services.io.s3_client import ClientS3


class IOManagerInput(IOManager):
    def handle_output(self, context: OutputContext, data: dict):
        s3_output_path = data.pop('s3_output_path')
        asset_data_document = AssetDataDocument(**data)
        s3_client: ClientS3 = context.resources.s3_resource
        s3_client.download_file(s3_path=asset_data_document.s3_path,
                                output_folder=asset_data_document.local_input_folder_path)
        Path(asset_data_document.local_input_folder_path).mkdir(parents=True, exist_ok=True)
        Path(asset_data_document.local_output_folder_path).mkdir(parents=True, exist_ok=True)
        with open(asset_data_document.local_output_file_path, 'w+') as file:
            for line in open(asset_data_document.local_input_file_path):
                data = json.loads(line)
                asset_document = asset_data_document.document_class.from_dict(data=data)
                if asset_document:
                    if asset_document.is_valid():
                        asset_document.process()
                        file.write(f'{json.dumps(asset_document.to_dict())}\n')
        s3_client.upload_file(local_path=asset_data_document.local_output_file_path,
                              s3_path=s3_output_path)

        for file_type, file_path in (
            ('input', asset_data_document.local_input_file_path),
            ('output', asset_data_document.local_output_file_path)
            ):
            try:
                os.remove(file_path)
                context.log.debug(f"Deleted temp {file_type} file {file_path}")
            except Exception as e:
                context.log.error(f"Failed to delete temp {file_type} file {file_path}: {e}")
        RunLogger().finish_run(s3_path=asset_data_document.s3_path)

    @abstractmethod
    def load_input(self, context: InputContext) -> list[dict]:
        pass


class IOManagerFieldsInput(IOManagerInput):
    def load_input(self, context: InputContext) -> list[str]:
        s3_client: ClientS3 = context.resources.s3_resource
        return s3_client.get_output_bounding_boxes()

class IOManagerBoundingBoxInput(IOManagerInput):
    def load_input(self, context: InputContext) -> list[str]:
        s3_client: ClientS3 = context.resources.s3_resource
        return s3_client.get_output_bounding_boxes()


# Im just reusing the components but I imagine the bounding box processing would store into PGIS or some queriable DB that doesnt depend on the box ID

@io_manager(required_resource_keys={'s3_resource'})
def io_manager_fields(context):
    return IOManagerFieldsInput()

@io_manager(required_resource_keys={'s3_resource'})
def io_manager_bounding_box(context):
    return IOManagerBoundingBoxInput()

