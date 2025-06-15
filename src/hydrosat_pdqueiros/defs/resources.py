
from dagster import resource

from hydrosat_pdqueiros.services.io.s3_client import ClientS3


@resource
def s3_resource(context):
    try:
        client = ClientS3()
        return client
    except Exception as e:
        context.log.error(e)
        return None
