drop table if exists thdata;
create table thdata (
    id integer primary key autoincrement,
    ts timestamp not null,
    temperature real not null,
    humidity real not null
);
