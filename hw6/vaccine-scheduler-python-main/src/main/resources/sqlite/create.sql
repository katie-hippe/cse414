CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash Binary(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Reservations (
    ApptID INTEGER PRIMARY KEY AUTOINCREMENT,
    cUsername varchar(255),
    pUsername varchar(255),
    Time date,
    Name varchar(255),
    FOREIGN KEY (cUsername) REFERENCES Caregivers(Username),
    FOREIGN KEY (pUsername) REFERENCES Patients(Username),
    FOREIGN KEY (Name) REFERENCES Vaccines(Name)
);