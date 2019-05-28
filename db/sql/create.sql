create table User (
  id integer primary key,
  username varchar(32) UNIQUE,
  email varchar(64) UNIQUE,
  name varchar(32),
  family_name varchar(32),
  phone varchar(32),
  address varchar(128),
  salt varchar(32),
  hash varchar(128),
  admin boolean
);

create table Room (
  id integer primary key,
  name varchar(64),
  type integer,
  capacity integer,
  description varchar(512),
  equipment_id integer,
  FOREIGN KEY (equipment_id) REFERENCES Equipment(id) ON DELETE CASCADE ON UPDATE CASCADE
);

create table Reservation (
  id integer primary key,
  user_id integer,
  room_id integer,
  date_begin date,
  date_end date,
  FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (room_id) REFERENCES Room(id) ON DELETE CASCADE ON UPDATE CASCADE
);


create table Session (
  id integer primary key,
  id_session varchar(32),
  email varchar(32),
  FOREIGN KEY (email) REFERENCES User(email) ON DELETE CASCADE ON UPDATE CASCADE
);


create table Equipment (
  id varchar(32) primary key,
  room_id integer,
  computer boolean,
  white_board boolean,
  sound_system boolean,
  projector boolean,
  FOREIGN KEY (room_id) REFERENCES Room(id) ON DELETE CASCADE ON UPDATE CASCADE
);

PRAGMA foreign_keys=on;