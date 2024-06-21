USE ai_project;

CREATE TABLE "Usuarios" 
(
ID_Usuario INT PRIMARY KEY IDENTITY,
NombreUsuario VARCHAR(20),
CorreoUsuario VARCHAR(30),
NombrePlan VARCHAR(14),
Contraseña VARCHAR(15)
);

CREATE TABLE "Planes"
(
ID_Plan INT PRIMARY KEY IDENTITY,
NombrePlan VARCHAR(15),
Descripcion VARCHAR(MAX),
Precio DECIMAL(10, 2)
);

CREATE TABLE "Transacciones"
(
ID_Transaccion INT PRIMARY KEY IDENTITY,
FechaTransaccion DATE DEFAULT GETDATE(),
NombrePlan VARCHAR (15),
MedioPago VARCHAR(15),
Precio DECIMAL(10, 2),
ID_Usuario INT REFERENCES "Usuarios"(ID_Usuario),
ID_Plan INT REFERENCES "Planes"(ID_Plan)
);

CREATE TABLE "Asesor_C" (
ID_Asesor_C INT PRIMARY KEY IDENTITY,
NombreAsesorC VARCHAR(30),
Descripcion VARCHAR(MAX),
ID_Usuario INT REFERENCES "Usuarios"(ID_Usuario)
);

CREATE TABLE "Chat_C"
(
ID_Chat_C INT PRIMARY KEY IDENTITY,
NombreChat VARCHAR(30),
partition_id AS CONCAT(ID_Usuario, '-', NombreChat),
ID_Usuario INT REFERENCES "Usuarios"(ID_Usuario),
ID_Asesor_C INT REFERENCES "Asesor_C"(ID_Asesor_C)
);

CREATE TABLE "Archivos" 
(
idArchivo INT PRIMARY KEY IDENTITY,
NombreArchivo VARCHAR(30),
TipoArchivo VARCHAR(100),
ID_Asesor_C INT REFERENCES "Asesor_C"(ID_Asesor_C),
archivo_datastax VARCHAR(40),
total_ids INT
);

CREATE TABLE "Asesor_H" 
(
ID_Asesor_H INT PRIMARY KEY IDENTITY,
dni INT,
NombreAsesorH VARCHAR(20),
ApellidoAsesorH VARCHAR(20),
CorreoAsesorH VARCHAR (30),
Especialidad VARCHAR(30),
Credencial VARCHAR(20),
Contraseña VARCHAR(14)
);

CREATE TABLE "Especialidades"
(
ID_Especialidad INT PRIMARY KEY IDENTITY,
Especialidad VARCHAR(20),
Credencial VARCHAR(20)
);

ALTER TABLE Chat_C
ADD SeguridadTipo INT;

CREATE TABLE "SeguridadTipo2"
(
ID_Seguridad_II INT PRIMARY KEY IDENTITY,
ID_Chat_C INT REFERENCES "Chat_C" (ID_Chat_C), 
Pin INT,
);

CREATE TABLE "SeguridadTipo3"
(
ID_Seguridad_III INT PRIMARY KEY IDENTITY,
ID_Chat_C INT REFERENCES "Chat_C" (ID_Chat_C), 
Pin INT,
Contrasena INT, 
);