use ai_project;

SELECT a.NombreAsesorC, a.Descripcion FROM Asesor_C as a WHERE a.ID_Usuario = 63;

SELECT c.NombreChat as NombreChat, c.partition_id AS partition_id FROM Chat_C as c WHERE c.ID_Usuario = 63;

