# Luxury Shoes Store — Microservicios

Proyecto académico: tienda de calzado de lujo implementada con arquitectura de microservicios.

---

## Arquitectura del sistema

El sistema está dividido en **3 microservicios independientes** que se comunican entre sí mediante HTTP:

```
[Navegador]
     |
     | :5002
     v
[store-service]  ——— :5001 ———> [auth-service]
     |                               (login, tokens)
     | :5003
     v
[user-service]
(perfiles, ordenes)
```

| Servicio | Puerto | Responsabilidad |
|---|---|---|
| auth-service | 5001 | Registro, login, verificación de tokens |
| store-service | 5002 | Catálogo, carrito, interfaz principal |
| user-service | 5003 | Perfiles de usuario, historial de órdenes |

Cada servicio tiene su propia base de datos SQLite independiente.

---

## Cómo ejecutar el proyecto

### Requisitos
- Python 3.11 o superior instalado

### Paso 1 — Instalar dependencias (una sola vez)

Abre **3 terminales** en VS Code (`Terminal > New Terminal`) y ejecuta en cada una:

**Terminal 1:**
```bash
cd auth-service
pip install -r requirements.txt
```

**Terminal 2:**
```bash
cd store-service
pip install -r requirements.txt
```

**Terminal 3:**
```bash
cd user-service
pip install -r requirements.txt
```

### Paso 2 — Ejecutar los servicios

Siempre en el mismo orden: primero auth, luego user, luego store.

**Terminal 1:**
```bash
cd auth-service
python app.py
```

**Terminal 2:**
```bash
cd user-service
python app.py
```

**Terminal 3:**
```bash
cd store-service
python app.py
```

### Paso 3 — Abrir en el navegador

```
http://localhost:5002
```

---

## Verificar que los servicios están corriendo

```
http://localhost:5001/health  → auth-service
http://localhost:5002/health  → store-service
http://localhost:5003/health  → user-service
```

---

## Estructura de archivos

```
luxury-shoes/
│
├── auth-service/
│   ├── app.py            ← Lógica de autenticación
│   ├── requirements.txt
│   └── auth.db           ← Se crea automáticamente al correr
│
├── store-service/
│   ├── app.py            ← Tienda, carrito, pagos, interfaz
│   └── requirements.txt
│
├── user-service/
│   ├── app.py            ← Perfiles y órdenes
│   ├── requirements.txt
│   └── users.db          ← Se crea automáticamente al correr
│
└── README.md
```

---

## Control de versiones con Git

```bash
# Inicializar el repositorio
git init
git branch -M main

# Primer commit
git add .
git commit -m "feat: estructura inicial del proyecto"

# Crear ramas por servicio
git checkout -b feature/auth-service
git add auth-service/
git commit -m "feat: agregar auth-service con login y tokens"

git checkout main
git checkout -b feature/store-service
git add store-service/
git commit -m "feat: agregar store-service con catalogo y carrito"

git checkout main
git checkout -b feature/user-service
git add user-service/
git commit -m "feat: agregar user-service con perfil y ordenes"

# Merge de ramas
git checkout main
git merge feature/auth-service
git merge feature/store-service
git merge feature/user-service

# Subir a GitHub
git remote add origin https://github.com/tu-usuario/luxury-shoes-store.git
git push -u origin main
```

---

## Flujo de comunicación entre servicios

1. El usuario entra en `store-service` (:5002)
2. Al hacer login, `store-service` llama a `auth-service /login` → recibe un token
3. Ese token se guarda en la sesión del navegador
4. Al confirmar un pago, `store-service` llama a `user-service /orders` con el token
5. `user-service` verifica el token llamando a `auth-service /verify` antes de guardar

---

## Pruebas del sistema

| Prueba | Qué hacer |
|---|---|
| Registro | Ir a `/register`, crear usuario nuevo |
| Login correcto | Ingresar con credenciales válidas |
| Login incorrecto | Ingresar con contraseña errónea — debe mostrar error |
| Catálogo y filtros | Filtrar productos por categoría |
| Carrito | Agregar productos, verificar totales |
| Pago | Completar orden, verificar mensaje de éxito |
| Comunicación entre servicios | Al pagar, `user-service` debe recibir la orden |

---

## Problemas encontrados y soluciones

**Problema:** Los servicios se conectaban entre sí con `localhost` pero fallaban.
**Solución:** Asegurarse de que los tres servicios estén corriendo antes de hacer peticiones.

**Problema:** La base de datos no se creaba en la carpeta correcta.
**Solución:** Ejecutar cada `app.py` desde dentro de su propia carpeta (`cd auth-service` antes de `python app.py`).

---

## Despliegue en Render.com

1. Subir el repositorio a GitHub
2. Entrar a [render.com](https://render.com) → New Web Service
3. Conectar el repositorio y configurar:
   - **Root Directory:** `auth-service`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
4. Repetir para `store-service` y `user-service`
5. En las variables de entorno de `store-service`, actualizar:
   - `AUTH_URL` = URL pública de auth-service en Render
   - `USER_URL` = URL pública de user-service en Render
