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
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Reservations (
    AppointmentID int,
    Dose varchar(255),
    pUsername varchar(255),
    cUsername varchar(255),
    Time date,
    PRIMARY KEY (AppointmentID),
    FOREIGN KEY (Dose) REFERENCES Vaccines(name),
    FOREIGN KEY (pUsername) REFERENCES Patients(Username),
    FOREIGN KEY (cUsername) REFERENCES Caregivers(Username)
);