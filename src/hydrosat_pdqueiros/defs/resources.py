import os

from dagster import resource

from hydrosat_pdqueiros.services.io.s3_client import ClientS3


def get_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value


@resource
def s3_resource(context):
    try:
        client = ClientS3(aws_access_key_id=get_env('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=get_env('AWS_SECRET_ACCESS_KEY'),
                         region_name=get_env('AWS_DEFAULT_REGION'),
                         bucket_name=get_env('S3_BUCKET'),
                         )
        return client
    except Exception as e:
        context.log.error(e)
        return None
