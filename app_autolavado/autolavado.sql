-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 30-08-2025 a las 02:43:23
-- Versión del servidor: 10.4.28-MariaDB
-- Versión de PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `autolavado`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL,
  `curp` varchar(15) DEFAULT NULL,
  `rfc` varchar(13) DEFAULT NULL,
  `folio` varchar(10) NOT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `id_usuario` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `codigo_verificacion`
--

CREATE TABLE `codigo_verificacion` (
  `id_codigo` int(11) NOT NULL,
  `codigo_verificacion` varchar(100) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  `estatus` bit(1) NOT NULL DEFAULT b'0',
  `id_usuario` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

--
-- Volcado de datos para la tabla `codigo_verificacion`
--

INSERT INTO `codigo_verificacion` (`id_codigo`, `codigo_verificacion`, `descripcion`, `fecha_registro`, `estatus`, `id_usuario`) VALUES
(3, '488851', NULL, '2025-08-23 07:51:05', b'0', 1),
(4, '307304', 'Restablecimiento de contraseña por correo', '2025-08-23 10:02:21', b'0', 1),
(5, '408348', 'Restablecimiento de contraseña por correo', '2025-08-23 10:43:36', b'0', 1),
(6, '006400', 'Restablecimiento de contraseña por correo', '2025-08-23 10:50:26', b'0', 1),
(7, '478266', 'Restablecimiento de contraseña por correo', '2025-08-23 14:07:02', b'0', 1),
(8, '670670', 'Restablecimiento de contraseña por correo', '2025-08-26 17:53:49', b'0', 1),
(9, '151372', 'Restablecimiento de contraseña por correo', '2025-08-26 18:22:22', b'0', 1),
(10, '016369', 'Restablecimiento de contraseña por correo', '2025-08-26 18:27:03', b'0', 1),
(11, '383781', 'Restablecimiento de contraseña por correo', '2025-08-28 20:00:36', b'0', 1),
(12, '341707', 'Restablecimiento de contraseña por correo', '2025-08-28 20:15:43', b'0', 1),
(13, '814897', 'Restablecimiento de contraseña por correo', '2025-08-28 20:18:04', b'0', 1),
(14, '637387', 'Restablecimiento de contraseña por correo', '2025-08-28 20:21:04', b'0', 1),
(15, '081669', 'Restablecimiento de contraseña por correo', '2025-08-28 20:44:27', b'0', 1),
(16, '442210', 'Restablecimiento de contraseña por correo', '2025-08-28 20:47:53', b'0', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `direcciones`
--

CREATE TABLE `direcciones` (
  `id_direccion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresas`
--

CREATE TABLE `empresas` (
  `id_empresa` int(11) NOT NULL,
  `key_empresa` varchar(100) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `razon_social` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

--
-- Volcado de datos para la tabla `empresas`
--

INSERT INTO `empresas` (`id_empresa`, `key_empresa`, `nombre`, `razon_social`) VALUES
(1, '123456789', 'Autolavado', 'autolavado S.A. de C.V.');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reservas`
--

CREATE TABLE `reservas` (
  `id_reserva` int(11) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_reserva` date NOT NULL,
  `hora_reserva` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id_rol`, `nombre`, `descripcion`, `fecha_registro`) VALUES
(1, 'Administrador', NULL, '2025-07-22 07:11:42');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sesiones`
--

CREATE TABLE `sesiones` (
  `id_sesion` int(11) NOT NULL,
  `direccion_ip` varchar(20) NOT NULL,
  `fecha_inicio` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_cierre` datetime DEFAULT NULL,
  `id_usuario` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

--
-- Volcado de datos para la tabla `sesiones`
--

INSERT INTO `sesiones` (`id_sesion`, `direccion_ip`, `fecha_inicio`, `fecha_cierre`, `id_usuario`) VALUES
(1, '', '2025-08-10 21:57:25', NULL, 1),
(2, '', '2025-08-11 07:17:45', NULL, 1),
(3, '201.162.241.197', '2025-08-15 20:35:08', NULL, 1),
(4, '38.58.174.86', '2025-08-19 17:40:27', NULL, 1),
(5, '38.58.174.86', '2025-08-26 18:26:07', NULL, 1),
(6, '38.58.174.86', '2025-08-28 20:18:48', NULL, 1),
(7, '38.58.174.86', '2025-08-28 20:21:34', NULL, 1),
(8, '38.58.174.86', '2025-08-28 20:22:17', NULL, 1),
(9, '38.58.174.86', '2025-08-29 06:54:18', NULL, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(150) NOT NULL,
  `nombre_completo` varchar(150) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `telefono` varchar(10) DEFAULT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  `secret_key` varchar(250) DEFAULT NULL,
  `twofa_activado` bit(1) NOT NULL DEFAULT b'0',
  `fecha_cambio_psw` datetime DEFAULT NULL,
  `estatus_change_psw` bit(1) NOT NULL DEFAULT b'0',
  `id_rol` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `username`, `password_hash`, `nombre_completo`, `correo`, `telefono`, `fecha_registro`, `secret_key`, `twofa_activado`, `fecha_cambio_psw`, `estatus_change_psw`, `id_rol`) VALUES
(1, 'gerardo', '$2b$12$wFtH4E8dxHgy/Ril1MEjXuOdAUeqFtL6JKt6/0Ktmd1djbPWB/sLW', 'Gerardo Garduño Martinez', 'gerardogar1212@gmail.com', '7121005750', '2025-07-22 07:12:33', NULL, b'0', '2025-08-28 20:48:11', b'0', 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`id_cliente`),
  ADD KEY `clientes_usuarios_FK` (`id_usuario`);

--
-- Indices de la tabla `codigo_verificacion`
--
ALTER TABLE `codigo_verificacion`
  ADD PRIMARY KEY (`id_codigo`),
  ADD KEY `codigo_verificacion_usuarios_FK` (`id_usuario`);

--
-- Indices de la tabla `direcciones`
--
ALTER TABLE `direcciones`
  ADD PRIMARY KEY (`id_direccion`),
  ADD KEY `direcciones_usuarios_FK` (`id_usuario`);

--
-- Indices de la tabla `empresas`
--
ALTER TABLE `empresas`
  ADD PRIMARY KEY (`id_empresa`);

--
-- Indices de la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD PRIMARY KEY (`id_reserva`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `sesiones`
--
ALTER TABLE `sesiones`
  ADD PRIMARY KEY (`id_sesion`),
  ADD KEY `sesiones_usuarios_FK` (`id_usuario`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `usuarios_unique` (`username`),
  ADD KEY `usuarios_roles_FK` (`id_rol`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `id_cliente` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `codigo_verificacion`
--
ALTER TABLE `codigo_verificacion`
  MODIFY `id_codigo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `direcciones`
--
ALTER TABLE `direcciones`
  MODIFY `id_direccion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `empresas`
--
ALTER TABLE `empresas`
  MODIFY `id_empresa` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `reservas`
--
ALTER TABLE `reservas`
  MODIFY `id_reserva` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `sesiones`
--
ALTER TABLE `sesiones`
  MODIFY `id_sesion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD CONSTRAINT `clientes_usuarios_FK` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `codigo_verificacion`
--
ALTER TABLE `codigo_verificacion`
  ADD CONSTRAINT `codigo_verificacion_usuarios_FK` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `direcciones`
--
ALTER TABLE `direcciones`
  ADD CONSTRAINT `direcciones_usuarios_FK` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `sesiones`
--
ALTER TABLE `sesiones`
  ADD CONSTRAINT `sesiones_usuarios_FK` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_roles_FK` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
