drop table if exists commands;
create table commands (
    id integer primary key autoincrement,
    command text not null,
    ts timestamp not null,
    user text not null
);
