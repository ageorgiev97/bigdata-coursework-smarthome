#!/usr/bin/python

import subprocess
import json
from colorama import Fore, Style
from pathlib import Path


def run(cmd: str):
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).wait()


def info(*args):
    print(f'[{Fore.CYAN}LOG{Style.RESET_ALL}]', *args)


def main():
    here = Path('/home/daniel/projects/BigData/')
    landing = here / 'landing'
    tmp = here / 'tmp'

    info(f'Processing landing directory: {landing.absolute()}')

    row_count = 0
    for path in landing.glob('*.json'):
        info(f'{path.absolute()}...')
        rows = []
        data = json.loads(path.read_text(encoding='utf8'))
        for k, v in data.items():
            v['id'] = k
            rows.append(v)

        tmp_path = tmp / path.name
        with tmp_path.open('w', encoding='utf8') as file:
            for row in rows:
                # NOTE@Daniel:
                #   Output formatting contains one record per line:
                #   { "id"=..., "entity_id"=..., "state"=..., ...}
                print(json.dumps(row), file=file)
        row_count += len(rows)

    files = list(tmp.glob('*.json'))
    if files:
        info(f'Uploading {row_count} records to hadoop...')
        files_string = ' '.join(f'"{file.absolute()}"' for file in files)
        run(f'hdfs dfs -put -f {files_string} /inbound')

    info('Ensuring that Hive tables are created...')
    hql = here / 'create.hql';
    run(f'hive -f "{hql.absolute()}"')

    info('Ensuring that the local MySQL database is properly set up...')
    run('mysql -u root -proot -e "create database if not exists SensorData;"')
    run(
        'mysql -u root -proot -e "'
        '    use SensorData;'
        '    create table if not exists SensorData('
        '        id          int,'
        '        created     timestamp,'
        '        entity      varchar(100),'
        '        previous_id int,'
        '        state float'
        '    )'
        '"'
    )
    
    info('Clearing SensorData mysql table...')
    run('mysql -u root -proot -e "use SensorData; delete from SensorData;"')

    info('Exporting new data to mysql...')
    run(
        'sqoop export '
        '--connect "jdbc:mysql://localhost:3306/SensorData" '
        '--username root '
        '--password root '
        '--table SensorData '
        '--export-dir /user/hive/warehouse/sensordata '
        '--update-key id '
        '--update-mode allowinsert'
    )


if __name__ == '__main__':
    main()
