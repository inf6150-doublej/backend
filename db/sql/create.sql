create table Users (
  id integer primary key,
  username varchar(32) UNIQUE,
  name varchar(32),
  family_name varchar(32),
  phone varchar(32),
  address varchar(128),
  email varchar(32) UNIQUE,
  salt varchar(32),
  hash varchar(128)
);

create table Salles (
  id integer primary key,
  name varchar(64),
  type integer,
  capacity integer,
  description varchar(512),
  pic_id integer,
  reservation_id integer,
  FOREIGN KEY (reservation_id) REFERENCES Reservations(id)
  ON DELETE CASCADE
  ON UPDATE CASCADE
);

create table Reservations (
  id integer primary key,
  user_id integer,
  salle_id integer,
  date_creation date,
  FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE ON UPDATE CASCADE
  FOREIGN KEY (salle_id) REFERENCES Salles(id) ON DELETE CASCADE ON UPDATE CASCADE
);

create table Sessions (
  id integer primary key,
  id_session varchar(32),
  username varchar(32)
);

create table Accounts (
  id integer primary key,
  username varchar(32) UNIQUE,
  email varchar(32) UNIQUE,
  token varchar(32),
  date_sent text
);

create table Pictures (
  pic_id varchar(32) primary key,
  img_data blob
);



