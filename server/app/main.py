import os
import hashlib
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from dodopayments import DodoPayments

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Header,
    Request,
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, EmailStr

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    DateTime,
    ForeignKey,
    text,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    Session,
)

from dotenv import load_dotenv


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

DODO_API_KEY = os.environ["DODO_PAYMENTS_API_KEY"]
DODO_WEBHOOK_KEY = os.environ["DODO_PAYMENTS_WEBHOOK_KEY"]
DODO_ENVIRONMENT = os.environ.get(
    "DODO_PAYMENTS_ENVIRONMENT",
    "live_mode",
)

API_BASE_URL = os.environ.get(
    "API_BASE_URL",
    "https://api.taxpreparertools.com",
)

WEBSITE_URL = os.environ.get(
    "WEBSITE_URL",
    "https://www.taxpreparertools.com",
)

PRODUCT_CODE = os.environ.get(
    "PRODUCT_CODE",
    "pdf-qbo-converter",
)

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

dodo = DodoPayments(
    bearer_token=DODO_API_KEY,
    environment=DODO_ENVIRONMENT,
)


# ============================================================
# PLAN CONFIGURATION
#
# quota_limit  = shared conversions allowed per billing period,
#                reset to 0 every time subscription.renewed fires.
#                None = unlimited conversions.
# max_activations = simultaneous installs allowed on one key.
#                None = unlimited users/machines on one key.
# ============================================================

PLANS = {
    "basic_monthly": {
        "product_id": os.environ["DODO_PRODUCT_BASIC_MONTHLY"],
        "quota_limit": int(os.environ.get("QUOTA_BASIC_MONTHLY", "10")),
        "max_activations": 1,
    },
    "basic_annual": {
        "product_id": os.environ["DODO_PRODUCT_BASIC_ANNUAL"],
        "quota_limit": int(os.environ.get("QUOTA_BASIC_ANNUAL", "120")),
        "max_activations": 1,
    },
    "pro_monthly": {
        "product_id": os.environ["DODO_PRODUCT_PRO_MONTHLY"],
        "quota_limit": int(os.environ.get("QUOTA_PRO_MONTHLY", "120")),
        "max_activations": None,
    },
    "pro_annual": {
        "product_id": os.environ["DODO_PRODUCT_PRO_ANNUAL"],
        "quota_limit": int(os.environ.get("QUOTA_PRO_ANNUAL", "1500")),
        "max_activations": None,
    },
}

# One-time top-up product: adds to quota_limit for the CURRENT
# period without resetting quota_used or touching activations.
REFILL_PRODUCT_ID = os.environ.get("DODO_PRODUCT_REFILL")
REFILL_QUOTA_BONUS = int(os.environ.get("REFILL_QUOTA_BONUS", "500"))

PLAN_BY_PRODUCT_ID = {
    config["product_id"]: name
    for name, config in PLANS.items()
}

# Fallback default expiry window if a subscription webhook doesn't
# carry next_billing_date for some reason (defensive, shouldn't
# normally trigger).
DEFAULT_EXPIRY_DAYS = 35


# ============================================================
# DATABASE
# ============================================================

class Base(DeclarativeBase):
    pass


class License(Base):

    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(primary_key=True)

    license_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True,
    )

    license_prefix: Mapped[str] = mapped_column(
        String(20), index=True,
    )

    plan: Mapped[str] = mapped_column(String(30))

    status: Mapped[str] = mapped_column(
        String(30), default="ACTIVE", index=True,
    )

    customer_email: Mapped[Optional[str]] = mapped_column(
        String(320), nullable=True,
    )

    dodo_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
    )

    dodo_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, unique=True, index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    max_activations: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
    )

    # --- shared usage quota (per license_key, not per machine) ---

    quota_limit: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
    )

    quota_used: Mapped[int] = mapped_column(
        Integer, default=0,
    )

    quota_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    activations = relationship(
        "Activation",
        back_populates="license",
        cascade="all, delete-orphan",
    )


class Activation(Base):

    __tablename__ = "activations"

    id: Mapped[int] = mapped_column(primary_key=True)

    license_id: Mapped[int] = mapped_column(
        ForeignKey("licenses.id"), index=True,
    )

    installation_id: Mapped[str] = mapped_column(
        String(128), index=True,
    )

    machine_hash: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True,
    )

    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    deactivated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    license = relationship("License", back_populates="activations")


class DodoWebhookEvent(Base):
    """Idempotency ledger, keyed on Dodo's `webhook-id` header
    (Standard Webhooks spec) rather than a field inside the body,
    since that's the value guaranteed unique per delivery."""

    __tablename__ = "dodo_webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    webhook_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True,
    )

    event_type: Mapped[str] = mapped_column(String(255))

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="TaxPreparerTools License API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBSITE_URL],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():
    return {"service": "TaxPreparerTools License API", "status": "online"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ============================================================
# LICENSE KEY HELPERS
# ============================================================

def generate_license_key():

    alphabet = string.ascii_uppercase + string.digits

    def block():
        return "".join(secrets.choice(alphabet) for _ in range(4))

    return f"TPP-{block()}-{block()}-{block()}-{block()}"


def normalize_license_key(value: str):
    return value.strip().upper().replace(" ", "")


def hash_license(value: str):
    normalized = normalize_license_key(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class CheckoutRequest(BaseModel):
    plan: str
    email: Optional[EmailStr] = None


class ActivateRequest(BaseModel):
    license_key: str
    installation_id: str
    machine_hash: Optional[str] = None
    product: str = PRODUCT_CODE
    version: str = "unknown"


class ValidateRequest(BaseModel):
    license_key: str
    installation_id: str
    product: str = PRODUCT_CODE


class DeactivateRequest(BaseModel):
    license_key: str
    installation_id: str


class ReportUsageRequest(BaseModel):
    license_key: str
    installation_id: str
    product: str = PRODUCT_CODE


# ============================================================
# INTERNAL LICENSE CREATION / LOOKUP
# ============================================================

def create_license(
    db: Session,
    plan: str,
    email: Optional[str] = None,
    dodo_customer_id: Optional[str] = None,
    dodo_subscription_id: Optional[str] = None,
    expires_at: Optional[datetime] = None,
):
    if plan not in PLANS:
        raise ValueError(f"Unknown plan: {plan}")

    config = PLANS[plan]
    raw_key = generate_license_key()
    now = datetime.now(timezone.utc)

    license_obj = License(
        license_hash=hash_license(raw_key),
        license_prefix=raw_key[:8],
        plan=plan,
        status="ACTIVE",
        customer_email=str(email) if email else None,
        dodo_customer_id=dodo_customer_id,
        dodo_subscription_id=dodo_subscription_id,
        created_at=now,
        expires_at=expires_at or (now + timedelta(days=DEFAULT_EXPIRY_DAYS)),
        max_activations=config["max_activations"],
        quota_limit=config["quota_limit"],
        quota_used=0,
        quota_period_start=now,
    )

    db.add(license_obj)
    db.commit()
    db.refresh(license_obj)

    return raw_key, license_obj


def find_license(db: Session, license_key: str):
    key_hash = hash_license(license_key)
    return (
        db.query(License)
        .filter(License.license_hash == key_hash)
        .first()
    )


def find_license_by_subscription(db: Session, subscription_id: str):
    return (
        db.query(License)
        .filter(License.dodo_subscription_id == subscription_id)
        .first()
    )


def effective_status(license_obj: License):
    now = datetime.now(timezone.utc)

    if license_obj.status == "REVOKED":
        return "REVOKED"

    if license_obj.expires_at <= now:
        return "EXPIRED"

    return license_obj.status


def quota_snapshot(license_obj: License):
    return {
        "quota_limit": license_obj.quota_limit,
        "quota_used": license_obj.quota_used,
        "quota_remaining": (
            None
            if license_obj.quota_limit is None
            else max(license_obj.quota_limit - license_obj.quota_used, 0)
        ),
    }


# ============================================================
# CHECKOUT
# ============================================================

@app.post("/v1/checkout/create")
def create_checkout(request: CheckoutRequest):

    plan = request.plan.lower().strip()

    if plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan.")

    config = PLANS[plan]

    params = {
        "product_cart": [
            {"product_id": config["product_id"], "quantity": 1}
        ],
        "return_url": WEBSITE_URL + "/success.html",
        "metadata": {
            "product": PRODUCT_CODE,
            "plan": plan,
        },
    }

    if request.email:
        params["customer"] = {"email": str(request.email)}

    try:
        session = dodo.checkout_sessions.create(**params)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return {
        "checkout_url": session.checkout_url,
        "session_id": session.session_id,
    }


# ============================================================
# ACTIVATE
# ============================================================

@app.post("/v1/license/activate")
def activate_license(request: ActivateRequest, db: Session = Depends(get_db)):

    if request.product != PRODUCT_CODE:
        raise HTTPException(status_code=400, detail="Incorrect product.")

    license_obj = find_license(db, request.license_key)

    if not license_obj:
        raise HTTPException(status_code=404, detail="Invalid license key.")

    status = effective_status(license_obj)

    if status != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail=f"License is {status.lower()}.",
        )

    existing = (
        db.query(Activation)
        .filter(
            Activation.license_id == license_obj.id,
            Activation.installation_id == request.installation_id,
            Activation.deactivated_at.is_(None),
        )
        .first()
    )

    if existing:
        existing.last_seen = datetime.now(timezone.utc)
        db.commit()

        return {
            "valid": True,
            "status": "ACTIVE",
            "plan": license_obj.plan,
            "expires_at": license_obj.expires_at.isoformat(),
            "activation_id": existing.id,
            "max_activations": license_obj.max_activations,
            **quota_snapshot(license_obj),
        }

    # max_activations = None means unlimited users/machines on
    # this key (Pro plans) -- skip the seat-limit check entirely.
    if license_obj.max_activations is not None:

        active_count = (
            db.query(Activation)
            .filter(
                Activation.license_id == license_obj.id,
                Activation.deactivated_at.is_(None),
            )
            .count()
        )

        if active_count >= license_obj.max_activations:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Activation limit reached. "
                    "Deactivate another computer "
                    "or contact TaxPreparerTools.com."
                ),
            )

    activation = Activation(
        license_id=license_obj.id,
        installation_id=request.installation_id,
        machine_hash=request.machine_hash,
        activated_at=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
    )

    db.add(activation)
    db.commit()
    db.refresh(activation)

    return {
        "valid": True,
        "status": "ACTIVE",
        "plan": license_obj.plan,
        "expires_at": license_obj.expires_at.isoformat(),
        "activation_id": activation.id,
        "max_activations": license_obj.max_activations,
        **quota_snapshot(license_obj),
    }


# ============================================================
# VALIDATE
# ============================================================

@app.post("/v1/license/validate")
def validate_license(request: ValidateRequest, db: Session = Depends(get_db)):

    if request.product != PRODUCT_CODE:
        raise HTTPException(status_code=400, detail="Incorrect product.")

    license_obj = find_license(db, request.license_key)

    if not license_obj:
        raise HTTPException(status_code=404, detail="Invalid license.")

    status = effective_status(license_obj)

    activation = (
        db.query(Activation)
        .filter(
            Activation.license_id == license_obj.id,
            Activation.installation_id == request.installation_id,
            Activation.deactivated_at.is_(None),
        )
        .first()
    )

    if not activation:
        raise HTTPException(
            status_code=403,
            detail="This computer is not activated.",
        )

    activation.last_seen = datetime.now(timezone.utc)
    db.commit()

    return {
        "valid": status == "ACTIVE",
        "status": status,
        "plan": license_obj.plan,
        "expires_at": license_obj.expires_at.isoformat(),
        "max_activations": license_obj.max_activations,
        **quota_snapshot(license_obj),
    }


# ============================================================
# REPORT USAGE  (called once per successful QBO export)
#
# Increments quota_used atomically, keyed on the LICENSE, not
# the installation -- so usage is correctly shared across every
# machine activated under a "Pro" (unlimited-users) key. Uses a
# single conditional UPDATE so concurrent exports from different
# users on the same key can't both slip past the cap in a race.
# ============================================================

@app.post("/v1/license/report-usage")
def report_usage(request: ReportUsageRequest, db: Session = Depends(get_db)):

    if request.product != PRODUCT_CODE:
        raise HTTPException(status_code=400, detail="Incorrect product.")

    license_obj = find_license(db, request.license_key)

    if not license_obj:
        raise HTTPException(status_code=404, detail="Invalid license.")

    if effective_status(license_obj) != "ACTIVE":
        raise HTTPException(status_code=403, detail="License is not active.")

    activation = (
        db.query(Activation)
        .filter(
            Activation.license_id == license_obj.id,
            Activation.installation_id == request.installation_id,
            Activation.deactivated_at.is_(None),
        )
        .first()
    )

    if not activation:
        raise HTTPException(
            status_code=403,
            detail="This computer is not activated.",
        )

    if license_obj.quota_limit is None:
        # Unlimited plan -- still record usage for visibility,
        # no cap to enforce.
        db.execute(
            text(
                "UPDATE licenses SET quota_used = quota_used + 1 "
                "WHERE id = :id"
            ),
            {"id": license_obj.id},
        )
        db.commit()
        db.refresh(license_obj)

        return {"allowed": True, **quota_snapshot(license_obj)}

    result = db.execute(
        text(
            "UPDATE licenses "
            "SET quota_used = quota_used + 1 "
            "WHERE id = :id AND quota_used < quota_limit "
            "RETURNING quota_used"
        ),
        {"id": license_obj.id},
    )
    row = result.fetchone()
    db.commit()

    if row is None:
        db.refresh(license_obj)
        return {
            "allowed": False,
            "error": "quota_exceeded",
            **quota_snapshot(license_obj),
        }

    db.refresh(license_obj)

    return {"allowed": True, **quota_snapshot(license_obj)}


# ============================================================
# DEACTIVATE
# ============================================================

@app.post("/v1/license/deactivate")
def deactivate_license(request: DeactivateRequest, db: Session = Depends(get_db)):

    license_obj = find_license(db, request.license_key)

    if not license_obj:
        raise HTTPException(status_code=404, detail="Invalid license.")

    activation = (
        db.query(Activation)
        .filter(
            Activation.license_id == license_obj.id,
            Activation.installation_id == request.installation_id,
            Activation.deactivated_at.is_(None),
        )
        .first()
    )

    if not activation:
        raise HTTPException(status_code=404, detail="Activation not found.")

    activation.deactivated_at = datetime.now(timezone.utc)
    db.commit()

    return {"success": True}


# ============================================================
# DODO PAYMENTS WEBHOOK
# ============================================================

@app.post("/v1/webhooks/dodo")
async def dodo_webhook(
    request: Request,
    db: Session = Depends(get_db),
    webhook_id: str = Header(None, alias="webhook-id"),
    webhook_signature: str = Header(None, alias="webhook-signature"),
    webhook_timestamp: str = Header(None, alias="webhook-timestamp"),
):

    payload = await request.body()

    if not (webhook_id and webhook_signature and webhook_timestamp):
        raise HTTPException(status_code=400, detail="Missing webhook headers.")

    try:
        event = dodo.webhooks.unwrap(
            payload,
            headers={
                "webhook-id": webhook_id,
                "webhook-signature": webhook_signature,
                "webhook-timestamp": webhook_timestamp,
            },
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

    # Idempotency: Dodo (and any Standard-Webhooks-compliant sender)
    # may redeliver the same webhook-id more than once.
    existing = (
        db.query(DodoWebhookEvent)
        .filter(DodoWebhookEvent.webhook_id == webhook_id)
        .first()
    )

    if existing:
        return {"received": True, "duplicate": True}

    db.add(
        DodoWebhookEvent(
            webhook_id=webhook_id,
            event_type=event.type,
            received_at=datetime.now(timezone.utc),
        )
    )

    data = event.data
    event_type = event.type

    metadata = getattr(data, "metadata", None) or {}
    product_from_metadata = metadata.get("product")
    plan_from_metadata = metadata.get("plan")

    subscription_id = getattr(data, "subscription_id", None)

    # --------------------------------------------------------
    # SUBSCRIPTION ACTIVE
    # First-time activation OR reactivation from on_hold.
    # --------------------------------------------------------

    if event_type == "subscription.active":

        if product_from_metadata == PRODUCT_CODE and plan_from_metadata in PLANS:

            license_obj = (
                find_license_by_subscription(db, subscription_id)
                if subscription_id else None
            )

            if license_obj:
                # Reactivation of a previously on_hold subscription.
                if license_obj.status != "REVOKED":
                    license_obj.status = "ACTIVE"
            else:
                customer = getattr(data, "customer", None)
                customer_email = getattr(customer, "email", None)
                customer_id = getattr(customer, "customer_id", None)

                next_billing = getattr(data, "next_billing_date", None)
                expires_at = (
                    datetime.fromisoformat(next_billing)
                    if next_billing
                    else None
                )

                key, license_obj = create_license(
                    db=db,
                    plan=plan_from_metadata,
                    email=customer_email,
                    dodo_customer_id=customer_id,
                    dodo_subscription_id=subscription_id,
                    expires_at=expires_at,
                )
                # In production: email `key` to customer_email here
                # (e.g. via your transactional email provider) rather
                # than relying on Dodo's own receipt.

    # --------------------------------------------------------
    # SUBSCRIPTION RENEWED
    # Fires every billing cycle alongside payment.succeeded.
    # This is the reset point for the shared conversion quota.
    # --------------------------------------------------------

    elif event_type == "subscription.renewed":

        license_obj = (
            find_license_by_subscription(db, subscription_id)
            if subscription_id else None
        )

        if license_obj:

            next_billing = getattr(data, "next_billing_date", None)

            if next_billing:
                license_obj.expires_at = datetime.fromisoformat(next_billing)

            license_obj.quota_used = 0
            license_obj.quota_period_start = datetime.now(timezone.utc)

            if license_obj.status != "REVOKED":
                license_obj.status = "ACTIVE"

    # --------------------------------------------------------
    # SUBSCRIPTION ON HOLD (renewal payment failed, recoverable)
    # --------------------------------------------------------

    elif event_type == "subscription.on_hold":

        license_obj = (
            find_license_by_subscription(db, subscription_id)
            if subscription_id else None
        )

        if license_obj and license_obj.status != "REVOKED":
            license_obj.status = "PAST_DUE"

    # --------------------------------------------------------
    # SUBSCRIPTION FAILED (terminal -- initial mandate never
    # succeeded, no license should exist/continue for this one)
    # --------------------------------------------------------

    elif event_type == "subscription.failed":

        license_obj = (
            find_license_by_subscription(db, subscription_id)
            if subscription_id else None
        )

        if license_obj:
            license_obj.status = "REVOKED"

    # --------------------------------------------------------
    # SUBSCRIPTION UPDATED (cancellation, plan change, etc.)
    # Mirrors the old Stripe behavior: don't cut off access
    # early -- expires_at remains the authoritative cutoff.
    # --------------------------------------------------------

    elif event_type == "subscription.updated":

        license_obj = (
            find_license_by_subscription(db, subscription_id)
            if subscription_id else None
        )

        if license_obj:

            dodo_status = getattr(data, "status", None)

            if dodo_status == "active" and license_obj.status != "REVOKED":
                license_obj.status = "ACTIVE"

    # --------------------------------------------------------
    # PAYMENT SUCCEEDED
    # Only acted on here for one-time refill top-up purchases;
    # subscription charges are handled via subscription.renewed.
    # --------------------------------------------------------

    elif event_type == "payment.succeeded":

        product_id = getattr(data, "product_id", None)

        if REFILL_PRODUCT_ID and product_id == REFILL_PRODUCT_ID:

            customer = getattr(data, "customer", None)
            customer_id = getattr(customer, "customer_id", None)

            license_obj = None

            if customer_id:
                license_obj = (
                    db.query(License)
                    .filter(License.dodo_customer_id == customer_id)
                    .order_by(License.id.desc())
                    .first()
                )

            if license_obj and license_obj.quota_limit is not None:
                license_obj.quota_limit += REFILL_QUOTA_BONUS

    db.commit()

    return {"received": True}


# ============================================================
# ADMIN AUTH
# ============================================================

def verify_admin(authorization: Optional[str]):

    if not authorization:
        raise HTTPException(status_code=401, detail="Admin authentication required.")

    if not authorization.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Invalid authentication.")

    import base64

    try:
        decoded = base64.b64decode(authorization[6:]).decode()
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication.")

    valid_username = secrets.compare_digest(username, ADMIN_USERNAME)
    valid_password = secrets.compare_digest(password, ADMIN_PASSWORD)

    if not (valid_username and valid_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")


# ============================================================
# ADMIN: CREATE LICENSE (manual grants / comps)
# ============================================================

class AdminCreateLicense(BaseModel):
    plan: str
    email: Optional[EmailStr] = None
    days: Optional[int] = None


@app.post("/v1/admin/licenses")
def admin_create_license(
    request: AdminCreateLicense,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    verify_admin(authorization)

    plan = request.plan.lower()

    if plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan.")

    expires_at = None
    if request.days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.days)

    key, license_obj = create_license(
        db=db,
        plan=plan,
        email=str(request.email) if request.email else None,
        expires_at=expires_at,
    )

    return {
        "license_key": key,
        "plan": plan,
        "expires_at": license_obj.expires_at.isoformat(),
        "max_activations": license_obj.max_activations,
        **quota_snapshot(license_obj),
    }


# ============================================================
# ADMIN: LIST LICENSES
# ============================================================

@app.get("/v1/admin/licenses")
def admin_list_licenses(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    verify_admin(authorization)

    licenses = (
        db.query(License)
        .order_by(License.id.desc())
        .limit(500)
        .all()
    )

    return [
        {
            "id": x.id,
            "prefix": x.license_prefix,
            "plan": x.plan,
            "status": effective_status(x),
            "email": x.customer_email,
            "expires_at": x.expires_at.isoformat(),
            "max_activations": x.max_activations,
            "activations": len(
                [a for a in x.activations if a.deactivated_at is None]
            ),
            **quota_snapshot(x),
        }
        for x in licenses
    ]


# ============================================================
# ADMIN: REVOKE
# ============================================================

@app.post("/v1/admin/licenses/{license_id}/revoke")
def admin_revoke(
    license_id: int,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    verify_admin(authorization)

    license_obj = db.query(License).filter(License.id == license_id).first()

    if not license_obj:
        raise HTTPException(status_code=404, detail="License not found.")

    license_obj.status = "REVOKED"
    db.commit()

    return {"success": True}


# ============================================================
# ADMIN: RESET ACTIVATIONS
# ============================================================

@app.post("/v1/admin/licenses/{license_id}/reset-activations")
def admin_reset_activations(
    license_id: int,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    verify_admin(authorization)

    license_obj = db.query(License).filter(License.id == license_id).first()

    if not license_obj:
        raise HTTPException(status_code=404, detail="License not found.")

    now = datetime.now(timezone.utc)

    for activation in license_obj.activations:
        if activation.deactivated_at is None:
            activation.deactivated_at = now

    db.commit()

    return {"success": True}


# ============================================================
# ADMIN: RESET QUOTA (manual override, e.g. support goodwill)
# ============================================================

@app.post("/v1/admin/licenses/{license_id}/reset-quota")
def admin_reset_quota(
    license_id: int,
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    verify_admin(authorization)

    license_obj = db.query(License).filter(License.id == license_id).first()

    if not license_obj:
        raise HTTPException(status_code=404, detail="License not found.")

    license_obj.quota_used = 0
    license_obj.quota_period_start = datetime.now(timezone.utc)
    db.commit()

    return {"success": True, **quota_snapshot(license_obj)}
