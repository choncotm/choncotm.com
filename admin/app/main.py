import hashlib
import os
import time
from datetime import datetime, timedelta, timezone

import bcrypt
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD_HASH = os.environ["ADMIN_PASSWORD_HASH"].encode()
SESSION_SECRET = os.environ["SESSION_SECRET"]
DATABASE_URL = os.environ["DATABASE_URL"]

COOKIE_NAME = "admin_session"
SESSION_MAX_AGE = 60 * 60  # 1h, enforced server-side regardless of cookie lifetime
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300

# key -> human label, shown as checkboxes on /admin/users
AVAILABLE_RESOURCES = [
    ("amazon_price_tracker", "Amazon Price Tracker — bot Telegram"),
]
RESOURCE_KEYS = {key for key, _label in AVAILABLE_RESOURCES}
RESOURCE_LABELS = dict(AVAILABLE_RESOURCES)

serializer = URLSafeTimedSerializer(SESSION_SECRET)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)
    path = Column(String(512), nullable=False, default="")
    target = Column(String(1024), nullable=True)
    referrer = Column(String(1024), nullable=True)
    visitor_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (UniqueConstraint("period_type", "period_label"),)

    id = Column(Integer, primary_key=True)
    period_type = Column(String(10), nullable=False)  # "monthly" or "yearly"
    period_label = Column(String(20), nullable=False)  # "2026-07" or "2026"
    total_pageviews = Column(Integer, nullable=False)
    unique_visitors = Column(Integer, nullable=False)
    top_pages = Column(JSON, nullable=False)
    top_clicks = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(60), nullable=False)
    is_owner = Column(Boolean, nullable=False, default=False)
    resources = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(engine)


def bootstrap_owner() -> None:
    """Seed the owner account from env vars on first run.

    Keeps existing .env files working with no manual migration step;
    further accounts are managed from /admin/users.
    """
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == ADMIN_USERNAME).first():
            return
        db.add(
            User(
                username=ADMIN_USERNAME,
                password_hash=ADMIN_PASSWORD_HASH.decode(),
                is_owner=True,
                resources=[],
            )
        )
        db.commit()
    finally:
        db.close()


bootstrap_owner()

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


def generate_report(period_type: str, start: datetime, end: datetime, label: str) -> None:
    db = SessionLocal()
    try:
        total_pageviews = (
            db.query(Event)
            .filter(
                Event.type == "pageview",
                Event.created_at >= start,
                Event.created_at < end,
            )
            .count()
        )
        unique_visitors = (
            db.query(Event.visitor_hash)
            .filter(
                Event.type == "pageview",
                Event.created_at >= start,
                Event.created_at < end,
                Event.visitor_hash.isnot(None),
            )
            .distinct()
            .count()
        )
        top_pages = (
            db.query(Event.path, func.count(Event.id))
            .filter(
                Event.type == "pageview",
                Event.created_at >= start,
                Event.created_at < end,
            )
            .group_by(Event.path)
            .order_by(func.count(Event.id).desc())
            .limit(10)
            .all()
        )
        top_clicks = (
            db.query(Event.target, func.count(Event.id))
            .filter(
                Event.type == "click",
                Event.created_at >= start,
                Event.created_at < end,
                Event.target.isnot(None),
            )
            .group_by(Event.target)
            .order_by(func.count(Event.id).desc())
            .limit(10)
            .all()
        )
        db.add(
            Report(
                period_type=period_type,
                period_label=label,
                total_pageviews=total_pageviews,
                unique_visitors=unique_visitors,
                top_pages=[[p, n] for p, n in top_pages],
                top_clicks=[[t, n] for t, n in top_clicks],
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()  # report for this period already exists
    finally:
        db.close()


def run_monthly_report() -> None:
    now = datetime.now(timezone.utc)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if this_month_start.month == 1:
        prev_month_start = this_month_start.replace(
            year=this_month_start.year - 1, month=12
        )
    else:
        prev_month_start = this_month_start.replace(month=this_month_start.month - 1)
    label = prev_month_start.strftime("%Y-%m")
    generate_report("monthly", prev_month_start, this_month_start, label)


def run_yearly_report() -> None:
    now = datetime.now(timezone.utc)
    this_year_start = now.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    prev_year_start = this_year_start.replace(year=this_year_start.year - 1)
    label = str(prev_year_start.year)
    generate_report("yearly", prev_year_start, this_year_start, label)


scheduler = BackgroundScheduler(timezone="UTC")
scheduler.add_job(run_monthly_report, CronTrigger(day=1, hour=0, minute=5))
scheduler.add_job(run_yearly_report, CronTrigger(month=1, day=1, hour=0, minute=10))
scheduler.start()

_failed_attempts: dict[str, tuple[int, float]] = {}


def get_client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def is_locked_out(ip: str) -> bool:
    entry = _failed_attempts.get(ip)
    if not entry:
        return False
    count, first_time = entry
    if time.time() - first_time >= LOCKOUT_SECONDS:
        _failed_attempts.pop(ip, None)
        return False
    return count >= MAX_ATTEMPTS


def record_failed_attempt(ip: str) -> None:
    count, first_time = _failed_attempts.get(ip, (0, time.time()))
    if time.time() - first_time >= LOCKOUT_SECONDS:
        count, first_time = 0, time.time()
    _failed_attempts[ip] = (count + 1, first_time)


def clear_attempts(ip: str) -> None:
    _failed_attempts.pop(ip, None)


def _cookie_username(request: Request) -> str | None:
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie:
        return None
    try:
        return serializer.loads(cookie, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def current_user(request: Request) -> User | None:
    username = _cookie_username(request)
    if not username:
        return None
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()


def require_owner(request: Request) -> User | None:
    """Returns the user if they're the owner, else None."""
    user = current_user(request)
    return user if user and user.is_owner else None


def require_resource(request: Request, key: str) -> User | None:
    """Returns the user if they're the owner or have this resource, else None."""
    user = current_user(request)
    if not user:
        return None
    if user.is_owner or key in (user.resources or []):
        return user
    return None


def landing_url(user: User) -> str:
    return "/admin/stats" if user.is_owner else "/admin/home"


@app.get("/admin", response_class=HTMLResponse)
def login_page(request: Request):
    user = current_user(request)
    if user:
        return RedirectResponse(landing_url(user), status_code=303)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None}
    )


@app.post("/admin/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    ip = get_client_ip(request)
    if is_locked_out(ip):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Trop de tentatives, réessaie plus tard."},
            status_code=429,
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        valid = user is not None and bcrypt.checkpw(
            password.encode(), user.password_hash.encode()
        )
        landing = landing_url(user) if valid else "/admin/stats"
    finally:
        db.close()

    if not valid:
        record_failed_attempt(ip)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Identifiants invalides."},
            status_code=401,
        )

    clear_attempts(ip)
    token = serializer.dumps(username)
    resp = RedirectResponse(landing, status_code=303)
    resp.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=True,
        samesite="strict",
        # no max_age: browser-session cookie, cleared when the browser closes.
        # server still enforces the 1h SESSION_MAX_AGE on the signed token.
    )
    return resp


@app.get("/admin/logout")
def logout():
    resp = RedirectResponse("/admin", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp


@app.get("/admin/home", response_class=HTMLResponse)
def home_page(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/admin", status_code=303)
    if user.is_owner:
        return RedirectResponse("/admin/stats", status_code=303)

    dashboards = [
        {"url": "/admin/bots/amazon-price-tracker", "label": RESOURCE_LABELS[key]}
        for key in (user.resources or [])
        if key in RESOURCE_KEYS
    ]
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "user": user, "dashboards": dashboards},
    )


@app.get("/admin/bots/amazon-price-tracker", response_class=HTMLResponse)
def bot_amazon_price_tracker_page(request: Request):
    user = require_resource(request, "amazon_price_tracker")
    if not user:
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "bot_placeholder.html",
        {
            "request": request,
            "user": user,
            "title": "Amazon Price Tracker",
        },
    )


@app.get("/admin/stats", response_class=HTMLResponse)
def stats_page(request: Request):
    if not require_owner(request):
        return RedirectResponse("/admin", status_code=303)

    since = datetime.now(timezone.utc) - timedelta(days=30)
    db = SessionLocal()
    try:
        total_pageviews = db.query(Event).filter(Event.type == "pageview").count()
        pageviews_30d = (
            db.query(Event)
            .filter(Event.type == "pageview", Event.created_at >= since)
            .count()
        )
        unique_visitors_30d = (
            db.query(Event.visitor_hash)
            .filter(
                Event.type == "pageview",
                Event.created_at >= since,
                Event.visitor_hash.isnot(None),
            )
            .distinct()
            .count()
        )
        top_pages = (
            db.query(Event.path, func.count(Event.id).label("n"))
            .filter(Event.type == "pageview", Event.created_at >= since)
            .group_by(Event.path)
            .order_by(func.count(Event.id).desc())
            .limit(10)
            .all()
        )
        top_clicks = (
            db.query(Event.target, func.count(Event.id).label("n"))
            .filter(
                Event.type == "click",
                Event.created_at >= since,
                Event.target.isnot(None),
            )
            .group_by(Event.target)
            .order_by(func.count(Event.id).desc())
            .limit(10)
            .all()
        )
        recent = db.query(Event).order_by(Event.created_at.desc()).limit(20).all()
    finally:
        db.close()

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "total_pageviews": total_pageviews,
            "pageviews_30d": pageviews_30d,
            "unique_visitors_30d": unique_visitors_30d,
            "top_pages": top_pages,
            "top_clicks": top_clicks,
            "recent": recent,
        },
    )


HISTORY_PAGE_SIZE = 50


@app.get("/admin/history", response_class=HTMLResponse)
def history_page(request: Request, page: int = 1):
    if not require_owner(request):
        return RedirectResponse("/admin", status_code=303)

    page = max(page, 1)
    offset = (page - 1) * HISTORY_PAGE_SIZE

    db = SessionLocal()
    try:
        total = db.query(Event).count()
        events = (
            db.query(Event)
            .order_by(Event.created_at.desc())
            .offset(offset)
            .limit(HISTORY_PAGE_SIZE)
            .all()
        )
    finally:
        db.close()

    total_pages = max((total + HISTORY_PAGE_SIZE - 1) // HISTORY_PAGE_SIZE, 1)

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "events": events,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


@app.get("/admin/reports", response_class=HTMLResponse)
def reports_page(request: Request):
    if not require_owner(request):
        return RedirectResponse("/admin", status_code=303)

    db = SessionLocal()
    try:
        reports = db.query(Report).order_by(Report.period_label.desc()).all()
    finally:
        db.close()

    monthly = [r for r in reports if r.period_type == "monthly"]
    yearly = [r for r in reports if r.period_type == "yearly"]

    return templates.TemplateResponse(
        "reports.html",
        {"request": request, "monthly": monthly, "yearly": yearly},
    )


@app.get("/admin/users", response_class=HTMLResponse)
def users_page(request: Request, error: str | None = None):
    if not require_owner(request):
        return RedirectResponse("/admin", status_code=303)

    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.username).all()
    finally:
        db.close()

    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
            "available_resources": AVAILABLE_RESOURCES,
            "error": error,
        },
    )


@app.post("/admin/users/create")
def create_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    resources: list[str] = Form([]),
):
    owner = require_owner(request)
    if not owner:
        return RedirectResponse("/admin", status_code=303)

    username = username.strip()
    granted = [r for r in resources if r in RESOURCE_KEYS]

    if not username or len(password) < 8:
        return RedirectResponse(
            "/admin/users?error=Nom+d%27utilisateur+requis+et+mot+de+passe+d%27au+moins+8+caract%C3%A8res.",
            status_code=303,
        )

    db = SessionLocal()
    try:
        db.add(
            User(
                username=username,
                password_hash=bcrypt.hashpw(
                    password.encode(), bcrypt.gensalt()
                ).decode(),
                is_owner=False,
                resources=granted,
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        return RedirectResponse(
            "/admin/users?error=Ce+nom+d%27utilisateur+existe+d%C3%A9j%C3%A0.",
            status_code=303,
        )
    finally:
        db.close()

    return RedirectResponse("/admin/users", status_code=303)


@app.post("/admin/users/{user_id}/update")
def update_user(
    request: Request,
    user_id: int,
    password: str = Form(""),
    resources: list[str] = Form([]),
):
    owner = require_owner(request)
    if not owner:
        return RedirectResponse("/admin", status_code=303)

    granted = [r for r in resources if r in RESOURCE_KEYS]

    if password and len(password) < 8:
        return RedirectResponse(
            "/admin/users?error=Le+mot+de+passe+doit+faire+au+moins+8+caract%C3%A8res.",
            status_code=303,
        )

    db = SessionLocal()
    try:
        target = db.query(User).filter(User.id == user_id).first()
        if target and not target.is_owner:
            target.resources = granted
            if password:
                target.password_hash = bcrypt.hashpw(
                    password.encode(), bcrypt.gensalt()
                ).decode()
            db.commit()
    finally:
        db.close()

    return RedirectResponse("/admin/users", status_code=303)


@app.post("/admin/users/{user_id}/delete")
def delete_user(request: Request, user_id: int):
    owner = require_owner(request)
    if not owner:
        return RedirectResponse("/admin", status_code=303)

    db = SessionLocal()
    try:
        target = db.query(User).filter(User.id == user_id).first()
        if target and not target.is_owner:
            db.delete(target)
            db.commit()
    finally:
        db.close()

    return RedirectResponse("/admin/users", status_code=303)


@app.post("/api/track")
async def track(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")

    event_type = body.get("type")
    if event_type not in ("pageview", "click"):
        raise HTTPException(status_code=400, detail="invalid type")

    path = str(body.get("path", ""))[:512]
    target = body.get("target")
    target = str(target)[:1024] if target else None
    referrer = (request.headers.get("referer") or "")[:1024] or None

    ip = get_client_ip(request)
    ua = request.headers.get("user-agent", "")
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    visitor_hash = hashlib.sha256(
        f"{ip}|{ua}|{day}|{SESSION_SECRET}".encode()
    ).hexdigest()[:32]

    db = SessionLocal()
    try:
        db.add(
            Event(
                type=event_type,
                path=path,
                target=target,
                referrer=referrer,
                visitor_hash=visitor_hash,
            )
        )
        db.commit()
    finally:
        db.close()

    return JSONResponse({"ok": True})
