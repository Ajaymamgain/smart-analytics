create table email (
    Email_Name text not null,
    Sent integer not null,
    Delivered integer not null,
    Hard_Bounced integer not null,
    soft_Bounced integer not null,
    Pending integer not null,
    Opened integer not null,
    clicked_Email integer not null,
    Unsubscribed integer not null,
    First_Activity datetime not null,
    Last_Activity datetime not null

);

create table users (
    id integer primary key autoincrement,
    name text not null,
    password text not null,
    admin boolean not null

);
