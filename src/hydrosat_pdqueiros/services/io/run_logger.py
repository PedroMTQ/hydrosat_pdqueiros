import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
import re
from hydrosat_pdqueiros.services.settings import TEMP


class RunLogger():
    '''This is not racing condition safe, but is ok for a POC. Later we would use something like postgres'''
    RUN_ENTRY = {
        's3_path': None,
        'start_time': None,
        'end_time': None,
                 }

    def __init__(self):
        Path(TEMP).mkdir(parents=True, exist_ok=True)
        self.__log_path = os.path.join(TEMP, 'runs.jsonl')
        Path(self.__log_path).touch()

    def update(self, s3_path: str, time_type: Literal['start_time', 'end_time']):
        add_entry = True
        data = []
        for line in open(self.__log_path):
            line_dict = json.loads(line)
            if line_dict['s3_path'] == s3_path:
                line_dict[time_type] = datetime.now().isoformat()
                if time_type == 'start_time':
                    line_dict['end_time'] = None
                add_entry = False
            data.append(line_dict)
        if add_entry:
            run_entry = dict(self.RUN_ENTRY)
            run_entry['s3_path'] = s3_path
            run_entry[time_type] = datetime.now().isoformat()
            data.append(run_entry)
        with open(self.__log_path, 'w+') as file:
            for line_dict in data:
                file.write(f'{json.dumps(line_dict)}\n')

    def start_run(self, s3_path: str):
        self.update(s3_path=s3_path, time_type='start_time')

    def finish_run(self, s3_path: str):
        self.update(s3_path=s3_path, time_type='end_time')


    def run_finished(self,
                     s3_path: Optional[str]=None,
                     pattern: Optional[re.Pattern]=None,):
        for line in open(self.__log_path):
            line_dict = json.loads(line)
            if s3_path:
                if line_dict['s3_path'] == s3_path and line_dict['end_time']:
                    return True
            elif pattern:
                if pattern.search(line_dict['s3_path']):
                    return True
        return False

if __name__ == '__main__':
    RunLogger().start_run('1')
    # print(RunLogger().run_finished('1'))
    # RunLogger().finish_run('1')
    # print(RunLogger().run_finished('1'))
    # RunLogger().finish_run('1')
    # print(RunLogger().run_finished('1'))
    # RunLogger().start_run('123/fields_2025-06-25.jsonl')
    # RunLogger().finish_run('123/fields_2025-06-25.jsonl')
    print(RunLogger().run_finished(pattern=re.compile('fields\/input\/01976a1225ca7e32a2daad543cb4391e\/fields_2025-06-02(.*)?\.jsonl')))
