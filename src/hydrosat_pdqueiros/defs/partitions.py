from dagster import DailyPartitionsDefinition

from hydrosat_pdqueiros.services.settings import START_DATE

DAILY_PARTITIONS = DailyPartitionsDefinition(start_date=START_DATE)
