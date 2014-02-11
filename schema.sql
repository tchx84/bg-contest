drop table if exists contest;
create table contest (
    id integer primary key autoincrement,
    person_name text not null,
    person_email text not null,
    person_age text not null,
    person_country text not null,
    person_photo text not null,
    bg_title text not null,
    bg_image text not null);
