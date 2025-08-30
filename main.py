from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import sqlite3
import hashlib
import uvicorn

app = FastAPI()

#  Add session middleware (secret key is important!)
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Static (CSS/JS/Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (HTML files)
templates = Jinja2Templates(directory="templates")  

#  Database connection for users
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password TEXT NOT NULL,
    date_of_birth TEXT NOT NULL
)
""")
conn.commit()

#  Signup page
@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request): 
    return templates.TemplateResponse("index.html", {"request": request})

#  Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})








#  Post page
@app.get("/post", response_class=HTMLResponse)
async def post_page(request: Request):
    return templates.TemplateResponse("post.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

#  Login function
@app.post("/logfunc")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
    user = cursor.fetchone()
    if user:
        request.session['user'] = user[1]  # Store first name in session
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid credentials"})    


# ---------------- POSTS DATABASE ----------------
def init_db():
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

#  for submitting post
@app.post("/submit-post",response_class=HTMLResponse) 
async def submit_post(request: Request, title: str = Form(...), content: str = Form(...),author: str = Form(...)):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)", (title, content, author))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/viewpost", status_code=303)
    
    
#  fetch and display posts
@app.get("/viewpost", response_class=HTMLResponse)
async def view_posts(request: Request):
    conn = sqlite3.connect("posts.db")
    conn.row_factory = sqlite3.Row  # To access columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("viewpost.html", {"request": request, "posts": posts})


# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
