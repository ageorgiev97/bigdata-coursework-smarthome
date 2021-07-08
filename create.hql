add jar /home/daniel/projects/hive/hcatalog/share/hcatalog/hive-hcatalog-core-3.1.2.jar;

drop table if exists RawData;
create external table if not exists RawData (
    id          string,
    created     string,
    entity_id   string,
    previous_id string,
    state       string
)
row format serde
    'org.apache.hive.hcatalog.data.JsonSerDe'
stored as TEXTFILE
location
    'hdfs://localhost/inbound/';

drop table if exists SensorData;
create table if not exists SensorData (
    Id         int,
    Created    string,
    Entity     string,
    PreviousId int,
    State      float
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n';

insert into table SensorData
select
    cast(RawData.id as int),
    from_unixtime(unix_timestamp(RawData.created, "yyyy-MM-dd HH-mm-ss")),
    RawData.entity_id,
    nvl(cast(RawData.previous_id as int), -1),
    nvl(cast(RawData.state as float), float('-696969'))
from RawData;
