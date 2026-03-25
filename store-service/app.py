"""
STORE SERVICE - Puerto 5002
Maneja: catalogo, carrito, pagos, interfaz web principal
Se comunica con:
  - auth-service (localhost:5001) para login/registro/verificacion
  - user-service (localhost:5003) para guardar ordenes
"""

from flask import Flask, render_template_string, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "luxury-shoes-2026-secret"

AUTH_URL = "http://localhost:5001"
USER_URL = "http://localhost:5003"

# ── Catalogo de productos ──────────────────────────────────────
PRODUCTS = [
    {"id": 1,  "name": "Nike Air Max Pro",         "price": 140, "category": "Running",
     "img": "https://images.unsplash.com/photo-1597248881519-db089d3744a5?w=400"},
    {"id": 2,  "name": "Adidas Ultraboost X",      "price": 160, "category": "Running",
     "img": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400"},
    {"id": 3,  "name": "Puma Velocity Nitro",      "price": 130, "category": "Running",
     "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"},
    {"id": 4,  "name": "Oxford Leather Black",     "price": 180, "category": "Formal",
     "img": "https://images.unsplash.com/photo-1614252369475-531eba835eb1?w=400"},
    {"id": 5,  "name": "Classic Brown Formal",     "price": 170, "category": "Formal",
     "img": "https://images.unsplash.com/photo-1610398752800-146f269dfcc8?w=400"},
    {"id": 6,  "name": "Summer White Sandals",     "price": 60,  "category": "Casual",
     "img": "https://images.unsplash.com/photo-1603808033192-082d6919d3e1?w=400"},
    {"id": 7,  "name": "Jordan Street Edition",    "price": 220, "category": "Sneakers",
     "img": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=400"},
    {"id": 8,  "name": "Minimalist White Sneakers","price": 110, "category": "Sneakers",
     "img": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=400"},
    {"id": 9,  "name": "Running Pro Black",        "price": 125, "category": "Running",
     "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"},
    {"id": 10, "name": "Elegant High Heels",       "price": 190, "category": "Formal",
     "img": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400"},
]

# ── HTML base compartido ───────────────────────────────────────
BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Luxury Shoes</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    * { font-family: 'Poppins', sans-serif; }
    body { background: #f5f5f0; min-height: 100vh; }

    /* Navbar */
    .navbar { background: #0a0a0a; padding: 14px 0; }
    .navbar-brand { color: #fff !important; font-weight: 600; letter-spacing: 3px; font-size: 1.1rem; }
    .nav-txt { color: rgba(255,255,255,.65); font-size: .85rem; }
    .nav-user { color: #fff; font-size: .85rem; font-weight: 500; }

    /* Hero */
    .hero {
      background: linear-gradient(rgba(0,0,0,.55), rgba(0,0,0,.5)),
                  url('https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=1400') center/cover;
      height: 300px; display:flex; align-items:center; justify-content:center; color:#fff;
    }
    .hero h1 { font-size: 2.5rem; font-weight: 600; letter-spacing: 2px; margin: 0; }
    .hero p  { opacity: .75; margin: 8px 0 0; font-size: .95rem; }

    /* Tarjetas de producto */
    .product-card { background:#fff; border:none; border-radius:16px; overflow:hidden;
                    transition:.3s; height:100%; }
    .product-card:hover { transform:translateY(-6px); box-shadow:0 20px 40px rgba(0,0,0,.12); }
    .product-card img { height:210px; object-fit:cover; width:100%; }
    .product-card .body { padding: 14px 16px 18px; text-align:center; }
    .product-card .name { font-weight:600; font-size:.9rem; margin-bottom:4px; }
    .product-card .price { color:#666; font-size:.85rem; margin-bottom:12px; }
    .badge-cat { font-size:.68rem; font-weight:400; background:#eee !important; color:#555 !important; margin-bottom:8px; }

    /* Carrito lateral */
    .cart-box { background:#fff; border-radius:16px; padding:22px;
                box-shadow:0 4px 20px rgba(0,0,0,.06); position:sticky; top:20px; }
    .cart-box h6 { font-weight:600; margin-bottom:14px; }
    .cart-item { display:flex; justify-content:space-between; font-size:.82rem;
                 padding:7px 0; border-bottom:1px solid #f0f0f0; }
    .cart-total { display:flex; justify-content:space-between; font-weight:600;
                  font-size:.95rem; margin-top:12px; }

    /* Formularios (login, registro, pago) */
    .form-card { background:#fff; border-radius:20px; padding:40px 36px; max-width:420px;
                 margin:0 auto; box-shadow:0 15px 50px rgba(0,0,0,.08); }
    .form-card h4 { font-weight:600; margin-bottom:4px; }
    .form-card .sub { color:#888; font-size:.85rem; margin-bottom:24px; }
    .form-control { border-radius:10px; border:1px solid #e0e0e0; font-size:.9rem; }
    .form-control:focus { border-color:#333; box-shadow:none; }
    .btn-dark { border-radius:10px; font-size:.9rem; }
    .btn-outline-dark { border-radius:10px; font-size:.85rem; }

    /* Filtros de categoria */
    .cat-btn { border-radius:20px; font-size:.8rem; padding:5px 14px; margin:0 4px 8px 0; }

    /* Badge de servicio (esquina inferior) */
    .svc-badge { position:fixed; bottom:12px; left:12px; background:rgba(0,0,0,.6);
                 color:#fff; font-size:.68rem; padding:4px 10px; border-radius:20px; z-index:999; }

    footer { margin-top:60px; padding:28px; text-align:center; color:#aaa; font-size:.82rem; }
  </style>
</head>
<body>
"""

def navbar(username=None):
    if username:
        user_html = f"""
          <span class="nav-user me-3">Hola, {username}</span>
          <a href="/logout" class="btn btn-outline-light btn-sm" style="border-radius:8px;font-size:.8rem">Salir</a>
        """
    else:
        user_html = """
          <a href="/login"    class="nav-txt me-3 text-decoration-none">Iniciar sesión</a>
          <a href="/register" class="btn btn-light btn-sm" style="border-radius:8px;font-size:.8rem">Registrarse</a>
        """
    return f"""
    <nav class="navbar">
      <div class="container d-flex align-items-center justify-content-between">
        <a class="navbar-brand" href="/store">LUXURY SHOES</a>
        <div class="d-flex align-items-center">{user_html}</div>
      </div>
    </nav>"""

def is_logged():
    return "token" in session and "username" in session

# ── Helpers de comunicacion con otros servicios ────────────────

def auth_register(username, password):
    try:
        r = requests.post(f"{AUTH_URL}/register",
                          json={"username": username, "password": password}, timeout=3)
        return r.status_code, r.json()
    except Exception:
        return 503, {"error": "auth-service no disponible. Asegurate de ejecutarlo."}

def auth_login(username, password):
    try:
        r = requests.post(f"{AUTH_URL}/login",
                          json={"username": username, "password": password}, timeout=3)
        return r.status_code, r.json()
    except Exception:
        return 503, {"error": "auth-service no disponible. Asegurate de ejecutarlo."}

def auth_logout(token):
    try:
        requests.post(f"{AUTH_URL}/logout", json={"token": token}, timeout=3)
    except Exception:
        pass

def user_save_order(token, cart, total):
    try:
        items_str = ", ".join([f"{p['name']} (${p['price']})" for p in cart])
        requests.post(f"{USER_URL}/orders",
                      json={"items": items_str, "total": total},
                      headers={"Authorization": token},
                      timeout=3)
    except Exception:
        pass

# ── Rutas ──────────────────────────────────────────────────────

@app.route("/health")
def health():
    from flask import jsonify
    return jsonify({"status": "ok", "service": "store-service", "puerto": 5002})

@app.route("/")
def index():
    return redirect(url_for("store") if is_logged() else url_for("login"))

# ── Login ──────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        status, data = auth_login(username, password)
        if status == 200:
            session["token"]    = data["token"]
            session["username"] = data["username"]
            session["cart"]     = []
            return redirect(url_for("store"))
        error = data.get("error", "Error al iniciar sesion")

    alert = f'<div class="alert alert-danger py-2 mb-3" style="font-size:.85rem">{error}</div>' if error else ""

    return BASE + navbar() + f"""
    <div class="container d-flex justify-content-center align-items-center" style="min-height:82vh">
      <div class="form-card w-100">
        <h4 class="text-center">Bienvenido</h4>
        <p class="sub text-center">Inicia sesion para continuar</p>
        {alert}
        <form method="POST">
          <input class="form-control mb-3" type="text"     name="username" placeholder="Usuario" required>
          <input class="form-control mb-3" type="password" name="password" placeholder="Contrasena" required>
          <button class="btn btn-dark w-100 py-2" type="submit">Entrar</button>
        </form>
        <p class="text-center mt-3" style="font-size:.83rem">
          No tienes cuenta? <a href="/register" class="text-dark fw-500">Registrate</a>
        </p>
      </div>
    </div>
    <div class="svc-badge">store-service :5002</div>
    </body></html>
    """

# ── Registro ───────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        status, data = auth_register(username, password)
        if status == 201:
            return redirect(url_for("login"))
        error = data.get("error", "Error al registrarse")

    alert = f'<div class="alert alert-danger py-2 mb-3" style="font-size:.85rem">{error}</div>' if error else ""

    return BASE + navbar() + f"""
    <div class="container d-flex justify-content-center align-items-center" style="min-height:82vh">
      <div class="form-card w-100">
        <h4 class="text-center">Crear cuenta</h4>
        <p class="sub text-center">Unete a Luxury Shoes</p>
        {alert}
        <form method="POST">
          <input class="form-control mb-3" type="text"     name="username" placeholder="Usuario" required>
          <input class="form-control mb-3" type="password" name="password" placeholder="Contrasena" required>
          <button class="btn btn-dark w-100 py-2" type="submit">Crear cuenta</button>
        </form>
        <p class="text-center mt-3" style="font-size:.83rem">
          Ya tienes cuenta? <a href="/login" class="text-dark">Inicia sesion</a>
        </p>
      </div>
    </div>
    <div class="svc-badge">store-service :5002</div>
    </body></html>
    """

# ── Logout ─────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    auth_logout(session.get("token", ""))
    session.clear()
    return redirect(url_for("login"))

# ── Tienda ─────────────────────────────────────────────────────
@app.route("/store")
def store():
    if not is_logged():
        return redirect(url_for("login"))

    username = session["username"]
    cart     = session.get("cart", [])
    total    = sum(p["price"] for p in cart)
    cat      = request.args.get("cat", "")

    filtered   = [p for p in PRODUCTS if not cat or p["category"] == cat]
    categories = sorted(set(p["category"] for p in PRODUCTS))

    # Botones de categoria
    active = "btn-dark" if not cat else "btn-outline-dark"
    cat_html = f'<a href="/store" class="btn {active} cat-btn">Todos</a>'
    for c in categories:
        a = "btn-dark" if cat == c else "btn-outline-dark"
        cat_html += f'<a href="/store?cat={c}" class="btn {a} cat-btn">{c}</a>'

    # Grilla de productos
    grid = ""
    for p in filtered:
        grid += f"""
        <div class="col-6 col-md-4 col-lg-3 mb-4">
          <div class="product-card shadow-sm">
            <img src="{p['img']}" alt="{p['name']}">
            <div class="body">
              <div><span class="badge badge-cat">{p['category']}</span></div>
              <div class="name">{p['name']}</div>
              <div class="price">${p['price']}</div>
              <a href="/add/{p['id']}" class="btn btn-dark btn-sm px-4">Agregar</a>
            </div>
          </div>
        </div>"""

    # Items del carrito
    if cart:
        items_html = "".join([
            f'<div class="cart-item"><span>{p["name"]}</span><span>${p["price"]}</span></div>'
            for p in cart
        ])
    else:
        items_html = '<p style="font-size:.82rem;color:#aaa;text-align:center">El carrito esta vacio</p>'

    return BASE + navbar(username) + f"""
    <div class="hero">
      <div class="text-center">
        <h1>Step Into Elegance</h1>
        <p>Coleccion exclusiva de calzado de lujo</p>
      </div>
    </div>

    <div class="container mt-5">
      <div class="row">

        <!-- Productos -->
        <div class="col-lg-9">
          <div class="mb-4">{cat_html}</div>
          <div class="row">{grid}</div>
        </div>

        <!-- Carrito -->
        <div class="col-lg-3 mt-4 mt-lg-0">
          <div class="cart-box">
            <h6>Carrito</h6>
            {items_html}
            <div class="cart-total"><span>Total</span><span>${total}</span></div>
            <a href="/pago"       class="btn btn-dark w-100 mt-3">Ir al pago</a>
            <a href="/cart/clear" class="btn btn-outline-dark w-100 mt-2 btn-sm">Vaciar</a>
          </div>
        </div>

      </div>
    </div>

    <footer>2026 Luxury Shoes Store &mdash; Proyecto Academico</footer>
    <div class="svc-badge">store-service :5002</div>
    </body></html>
    """

# ── Agregar al carrito ─────────────────────────────────────────
@app.route("/add/<int:pid>")
def add_to_cart(pid):
    if not is_logged():
        return redirect(url_for("login"))
    cart = session.get("cart", [])
    p    = next((x for x in PRODUCTS if x["id"] == pid), None)
    if p:
        cart.append(p)
        session["cart"] = cart
    return redirect(url_for("store"))

@app.route("/cart/clear")
def clear_cart():
    session["cart"] = []
    return redirect(url_for("store"))

# ── Pago ───────────────────────────────────────────────────────
@app.route("/pago", methods=["GET", "POST"])
def pago():
    if not is_logged():
        return redirect(url_for("login"))

    username = session["username"]
    cart     = session.get("cart", [])
    total    = sum(p["price"] for p in cart)

    if request.method == "POST":
        # Comunicacion con user-service: guardar la orden
        user_save_order(session.get("token", ""), cart, total)
        session["cart"] = []
        return BASE + navbar(username) + """
        <div class="container d-flex justify-content-center align-items-center" style="min-height:82vh">
          <div class="form-card text-center">
            <div style="font-size:3.5rem">🎉</div>
            <h3 class="mt-3 fw-bold">Orden exitosa</h3>
            <p style="color:#888">Tus zapatos de lujo estan en camino.</p>
            <a href="/store" class="btn btn-dark px-5 mt-2">Seguir comprando</a>
          </div>
        </div>
        <div class="svc-badge">store-service :5002</div>
        </body></html>
        """

    items_html = "".join([
        f'<li class="list-group-item d-flex justify-content-between" style="font-size:.85rem">'
        f'<span>{p["name"]}</span><span>${p["price"]}</span></li>'
        for p in cart
    ]) or '<li class="list-group-item text-muted" style="font-size:.85rem">Carrito vacio</li>'

    return BASE + navbar(username) + f"""
    <div class="container d-flex justify-content-center align-items-center" style="min-height:85vh">
      <div class="form-card" style="max-width:460px">
        <h4 class="text-center mb-1">Pago seguro</h4>
        <p class="sub text-center">Revisa tu orden y completa el pago</p>
        <ul class="list-group mb-3">{items_html}</ul>
        <div class="d-flex justify-content-between fw-semibold mb-4">
          <span>Total</span><span>${total}</span>
        </div>
        <form method="POST">
          <input class="form-control mb-3" type="text" placeholder="Nombre en la tarjeta" required>
          <input class="form-control mb-3" type="text" placeholder="Numero de tarjeta"     required>
          <input class="form-control mb-3" type="text" placeholder="Direccion de envio"    required>
          <button class="btn btn-dark w-100 py-2">Confirmar pago</button>
        </form>
      </div>
    </div>
    <div class="svc-badge">store-service :5002</div>
    </body></html>
    """

if __name__ == "__main__":
    print(">>> store-service corriendo en http://localhost:5002")
    app.run(port=5002, debug=True)
