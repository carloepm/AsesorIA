SELECT NombreArchivo FROM Usuarios as u
INNER JOIN Asesor_C as ac
ON u.ID_Usuario = ac.ID_Usuario
INNER JOIN Archivos as ar
ON ac.ID_Asesor_C = ar.ID_Asesor_C
WHERE u.CorreoUsuario = 'nico.sp903@gmail.com' and ac.ID_Asesor_C = 1

/* LA IDEA ES PODES HACER UN FILTRO POR USUARIO Y NOMBRE DE ASESOR*/
