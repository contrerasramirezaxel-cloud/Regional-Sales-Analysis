-- ==================================================
-- PROYECTO: Análisis y Automatización de Ventas Regionales
-- PAÍSES: Colombia, Costa Rica y México
-- HERRAMIENTA: SQL Server 2022
-- CÓDIGO 100% FUNCIONAL, SIN ERRORES Y LISTO PARA PORTAFOLIO
-- ==================================================

-- ==================================================
-- PASO 1: ELIMINAR OBJETOS SI EXISTEN (EVITA ERRORES DE DUPLICIDAD)
-- ==================================================
IF OBJECT_ID('vw_VentasAnalizadas', 'V') IS NOT NULL
    DROP VIEW vw_VentasAnalizadas;
GO

IF OBJECT_ID('Ventas', 'U') IS NOT NULL
    DROP TABLE Ventas;
GO

IF OBJECT_ID('Productos', 'U') IS NOT NULL
    DROP TABLE Productos;
GO

IF OBJECT_ID('Sucursales', 'U') IS NOT NULL
    DROP TABLE Sucursales;
GO

-- ==================================================
-- PASO 2: CREACIÓN DE TABLAS
-- ==================================================

-- Tabla: Productos
CREATE TABLE Productos (
    id_producto INT PRIMARY KEY IDENTITY(1,1),
    nombre_producto VARCHAR(500) NOT NULL,
    categoria VARCHAR(50),
    precio_unitario DECIMAL(10,2),
    costo_unitario DECIMAL(10,2),
    estado VARCHAR(20) -- Valores permitidos: 'Activo', 'Descontinuado'
);
GO

-- Tabla: Sucursales
CREATE TABLE Sucursales (
    id_sucursal INT PRIMARY KEY IDENTITY(1,1),
    nombre_sucursal VARCHAR(100) NOT NULL,
    pais VARCHAR(50), -- Valores permitidos: 'Colombia', 'Costa Rica', 'México'
    ciudad VARCHAR(50),
    zona_horaria VARCHAR(50)
);
GO

-- Tabla: Ventas
CREATE TABLE Ventas (
    id_venta INT PRIMARY KEY IDENTITY(1,1),
    id_producto INT,
    id_sucursal INT,
    fecha_venta DATETIME2,
    cantidad_vendida INT,
    monto_total DECIMAL(12,2),
    tipo_pago VARCHAR(30),
    estado_venta VARCHAR(30), -- Valores permitidos: 'Completada', 'Anulada', 'Pendiente'

    -- Claves foráneas para integridad de datos
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_sucursal) REFERENCES Sucursales(id_sucursal)
);
GO

-- ==================================================
-- PASO 3: CARGA DE DATOS DE EJEMPLO
-- ==================================================

-- Insertar sucursales
INSERT INTO Sucursales (nombre_sucursal, pais, ciudad, zona_horaria)
VALUES
    -- Colombia
    ('Sucursal Bogotá Centro', 'Colombia', 'Bogotá', 'UTC-5'),
    ('Sucursal Medellín', 'Colombia', 'Medellín', 'UTC-5'),
    -- Costa Rica
    ('Sucursal San José Principal', 'Costa Rica', 'San José', 'UTC-6'),
    ('Sucursal Heredia', 'Costa Rica', 'Heredia', 'UTC-6'),
    -- México
    ('Sucursal Ciudad de México Sur', 'México', 'Ciudad de México', 'UTC-6'),
    ('Sucursal Guadalajara', 'México', 'Guadalajara', 'UTC-6');
GO

-- Insertar productos
INSERT INTO Productos (nombre_producto, categoria, precio_unitario, costo_unitario, estado)
VALUES
    ('Laptop Empresarial Pro', 'Tecnología', 1250.00, 890.50, 'Activo'),
    ('Teléfono Inteligente X200', 'Tecnología', 680.00, 420.30, 'Activo'),
    ('Televisor 55 Pulgadas 4K', 'Electrónica', 950.00, 670.80, 'Activo'),
    ('Nevera Automática', 'Línea Blanca', 1450.00, 980.20, 'Activo'),
    ('Lavadora Inteligente', 'Línea Blanca', 890.00, 560.40, 'Activo'),
    ('Auriculares Inalámbricos', 'Accesorios', 180.00, 95.60, 'Activo'),
    ('Cámara Profesional', 'Fotografía', 2100.00, 1450.70, 'Activo'),
    ('Tablet Educativa', 'Tecnología', 350.00, 210.90, 'Activo');
GO

-- Insertar ventas
INSERT INTO Ventas (id_producto, id_sucursal, fecha_venta, cantidad_vendida, monto_total, tipo_pago, estado_venta)
VALUES
    -- Ventas Colombia
    (1, 1, DATEADD(MONTH, -3, GETDATE()), 2, 2500.00, 'Tarjeta Crédito', 'Completada'),
    (3, 1, DATEADD(MONTH, -2, GETDATE()), 1, 950.00, 'Efectivo', 'Completada'),
    (2, 2, DATEADD(MONTH, -1, GETDATE()), 3, 2040.00, 'Transferencia', 'Completada'),
    (5, 2, DATEADD(MONTH, -4, GETDATE()), 1, 890.00, 'Tarjeta Débito', 'Completada'),
    
    -- Ventas Costa Rica
    (4, 3, DATEADD(MONTH, -2, GETDATE()), 1, 1450.00, 'Tarjeta Crédito', 'Completada'),
    (6, 3, DATEADD(MONTH, -1, GETDATE()), 4, 720.00, 'Efectivo', 'Completada'),
    (1, 4, DATEADD(MONTH, -3, GETDATE()), 1, 1250.00, 'Transferencia', 'Completada'),
    (7, 4, DATEADD(MONTH, -5, GETDATE()), 1, 2100.00, 'Tarjeta Crédito', 'Completada'),
    
    -- Ventas México
    (8, 5, DATEADD(MONTH, -1, GETDATE()), 2, 700.00, 'Tarjeta Débito', 'Completada'),
    (2, 5, DATEADD(MONTH, -2, GETDATE()), 2, 1360.00, 'Efectivo', 'Completada'),
    (3, 6, DATEADD(MONTH, -4, GETDATE()), 2, 1900.00, 'Transferencia', 'Completada'),
    (5, 6, DATEADD(MONTH, -1, GETDATE()), 1, 890.00, 'Tarjeta Crédito', 'Completada');
GO

-- ==================================================
-- PASO 4: CREACIÓN DE LA VISTA (AHORA SIN ERRORES)
-- ==================================================
CREATE VIEW vw_VentasAnalizadas AS
SELECT 
    v.id_venta,
    p.id_producto,
    p.nombre_producto,
    p.categoria,
    s.id_sucursal,
    s.nombre_sucursal,
    s.pais,
    s.ciudad,
    v.fecha_venta,
    -- Desglose temporal
    YEAR(v.fecha_venta) AS anio,
    MONTH(v.fecha_venta) AS mes,
    DATENAME(MONTH, v.fecha_venta) AS nombre_mes,
    DATEPART(QUARTER, v.fecha_venta) AS trimestre,
    v.cantidad_vendida,
    v.monto_total,
    -- Cálculo de rentabilidad seguro
    (v.monto_total - (p.costo_unitario * v.cantidad_vendida)) AS margen_ganancia,
    ROUND(
        ((v.monto_total - (p.costo_unitario * v.cantidad_vendida)) / NULLIF(v.monto_total, 0)) * 100, 
    2) AS porcentaje_margen,
    v.tipo_pago,
    -- Clasificación de venta
    CASE 
        WHEN v.monto_total < 100 THEN 'Venta Pequeña'
        WHEN v.monto_total BETWEEN 100 AND 500 THEN 'Venta Mediana'
        ELSE 'Venta Grande'
    END AS tamano_venta,
    v.estado_venta
FROM Ventas v
INNER JOIN Productos p 
    ON v.id_producto = p.id_producto
INNER JOIN Sucursales s 
    ON v.id_sucursal = s.id_sucursal
WHERE 
    v.estado_venta = 'Completada'
    AND p.estado = 'Activo'
    AND s.pais IN ('Colombia', 'Costa Rica', 'México')
    AND v.fecha_venta >= DATEADD(YEAR, -2, GETDATE());
GO

-- ==================================================
-- ✅ VERIFICACIÓN Y RESULTADOS FINALES
-- ==================================================

-- Consulta 1: Listado de sucursales
SELECT 
    id_sucursal AS [ID Sucursal],
    nombre_sucursal AS [Nombre Sucursal],
    pais AS [País],
    ciudad AS [Ciudad],
    zona_horaria AS [Zona Horaria]
FROM Sucursales
ORDER BY pais, ciudad;
GO

-- Consulta 2: Ventas totales por país
SELECT 
    pais AS [País],
    COUNT(id_venta) AS [Cantidad de Ventas],
    SUM(monto_total) AS [Monto Total Ventas],
    ROUND(AVG(monto_total), 2) AS [Promedio por Venta]
FROM vw_VentasAnalizadas
GROUP BY pais
ORDER BY [Monto Total Ventas] DESC;
GO

-- Consulta 3: Productos más vendidos
SELECT 
    categoria AS [Categoría],
    nombre_producto AS [Producto],
    SUM(cantidad_vendida) AS [Unidades Vendidas],
    SUM(monto_total) AS [Valor Total Ventas]
FROM vw_VentasAnalizadas
GROUP BY categoria, nombre_producto
ORDER BY [Valor Total Ventas] DESC;
GO

