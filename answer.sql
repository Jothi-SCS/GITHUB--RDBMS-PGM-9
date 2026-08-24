
DROP DATABASE IF EXISTS CollegeDB;

CREATE DATABASE CollegeDB;

USE CollegeDB;

CREATE TABLE Department (
    DepartmentID INT NOT NULL,
    DepartmentName VARCHAR(50),
    PRIMARY KEY (DepartmentID)
);

CREATE TABLE Student (
    StudentID INT NOT NULL,
    StudentName VARCHAR(50),
    DepartmentID INT NOT NULL,
    PRIMARY KEY (StudentID),
    FOREIGN KEY (DepartmentID)
        REFERENCES Department(DepartmentID)
);

INSERT INTO Department (DepartmentID, DepartmentName)
VALUES
(101, 'Computer Science'),
(102, 'Mathematics'),
(103, 'Physics');

INSERT INTO Student (StudentID, StudentName, DepartmentID)
VALUES
(1001, 'Arun', 101),
(1002, 'Divya', 102),
(1003, 'Karthik', 101),
(1004, 'Nisha', 103);
