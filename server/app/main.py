import os
import hashlib
import secrets
import string
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import stripe

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
    Boolean,
    Text,
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

STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

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

stripe.api_key = STRIPE_SECRET_KEY


# ============================================================
# PLAN CONFIGURATION
# ============================================================

PLANS = {
    "monthly": {
        "price_id": os.environ["STRIPE_PRICE_MONTHLY"],
        "days": int(
            os.environ.get(
                "LICENSE_DAYS_MONTHLY",
                "30",
            )
        ),
        "max_activations": int(
            os.environ.get(
                "MAX_ACTIVATIONS_MONTHLY",
                "1",
            )
        ),
    },

    "yearly": {
        "price_id": os.environ["STRIPE_PRICE_YEARLY"],
        "days": int(
            os.environ.get(
                "LICENSE_DAYS_YEARLY",
                "365",
            )
        ),
        "max_activations": int(
            os.environ.get(
                "MAX_ACTIVATIONS_YEARLY",
                "1",
            )
        ),
    },

    "pro": {
        "price_id": os.environ["STRIPE_PRICE_PRO"],
        "days": int(
            os.environ.get(
                "LICENSE_DAYS_PRO",
                "365",
            )
        ),
        "max_activations": int(
            os.environ.get(
                "MAX_ACTIVATIONS_PRO",
                "3",
            )
        ),
    },
}


# ============================================================
# DATABASE
# ============================================================

class Base(DeclarativeBase):
    pass


class License(Base):

    __tablename__ = "licenses"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    license_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
    )

    license_prefix: Mapped[str] = mapped_column(
        String(20),
        index=True,
    )

    plan: Mapped[str] = mapped_column(
        String(30)
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="ACTIVE",
        index=True,
    )

    customer_email: Mapped[Optional[str]] = mapped_column(
        String(320),
        nullable=True,
    )

    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    stripe_checkout_session_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    max_activations: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    activations = relationship(
        "Activation",
        back_populates="license",
        cascade="all, delete-orphan",
    )


class Activation(Base):

    __tablename__ = "activations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    license_id: Mapped[int] = mapped_column(
        ForeignKey("licenses.id"),
        index=True,
    )

    installation_id: Mapped[str] = mapped_column(
        String(128),
        index=True,
    )

    machine_hash: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
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
        DateTime(timezone=True),
        nullable=True,
    )

    license = relationship(
        "License",
        back_populates="activations",
    )


class StripeEvent(Base):

    __tablename__ = "stripe_events"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    stripe_event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(255)
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


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
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        WEBSITE_URL,
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():

    Base.metadata.create_all(
        bind=engine
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "service": "TaxPreparerTools License API",
        "status": "online",
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
    }


# ============================================================
# LICENSE KEY
# ============================================================

def generate_license_key():

    alphabet = (
        string.ascii_uppercase
        + string.digits
    )

    def block():

        return "".join(
            secrets.choice(alphabet)
            for _ in range(4)
        )

    return (
        "TPP-"
        + block()
        + "-"
        + block()
        + "-"
        + block()
        + "-"
        + block()
    )


def normalize_license_key(
    value: str
):

    return (
        value
        .strip()
        .upper()
        .replace(" ", "")
    )


def hash_license(
    value: str
):

    normalized = normalize_license_key(
        value
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


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


# ============================================================
# INTERNAL LICENSE CREATION
# ============================================================

def create_license(
    db: Session,
    plan: str,
    email: Optional[str] = None,
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
    stripe_checkout_session_id: Optional[str] = None,
):

    if plan not in PLANS:

        raise ValueError(
            f"Unknown plan: {plan}"
        )

    raw_key = generate_license_key()

    now = datetime.now(
        timezone.utc
    )

    config = PLANS[plan]

    expires = (
        now
        + timedelta(
            days=config["days"]
        )
    )

    license_obj = License(

        license_hash=hash_license(
            raw_key
        ),

        license_prefix=raw_key[:8],

        plan=plan,

        status="ACTIVE",

        customer_email=(
            str(email)
            if email
            else None
        ),

        stripe_customer_id=(
            stripe_customer_id
        ),

        stripe_subscription_id=(
            stripe_subscription_id
        ),

        stripe_checkout_session_id=(
            stripe_checkout_session_id
        ),

        created_at=now,

        expires_at=expires,

        max_activations=(
            config["max_activations"]
        ),
    )

    db.add(
        license_obj
    )

    db.commit()

    db.refresh(
        license_obj
    )

    return raw_key, license_obj


# ============================================================
# LICENSE LOOKUP
# ============================================================

def find_license(
    db: Session,
    license_key: str,
):

    key_hash = hash_license(
        license_key
    )

    return (
        db.query(License)
        .filter(
            License.license_hash
            == key_hash
        )
        .first()
    )


# ============================================================
# LICENSE STATUS
# ============================================================

def effective_status(
    license_obj: License
):

    now = datetime.now(
        timezone.utc
    )

    if license_obj.status == "REVOKED":
        return "REVOKED"

    if license_obj.expires_at <= now:
        return "EXPIRED"

    return license_obj.status


# ============================================================
# CHECKOUT
# ============================================================

@app.post("/v1/checkout/create")
def create_checkout(
    request: CheckoutRequest
):

    plan = request.plan.lower().strip()

    if plan not in PLANS:

        raise HTTPException(
            status_code=400,
            detail="Invalid plan.",
        )

    config = PLANS[plan]

    metadata = {
        "product": PRODUCT_CODE,
        "plan": plan,
    }

    params = {

        "mode": "subscription",

        "line_items": [
            {
                "price": config["price_id"],
                "quantity": 1,
            }
        ],

        "success_url": (
            WEBSITE_URL
            + "/success.html"
            + "?session_id={CHECKOUT_SESSION_ID}"
        ),

        "cancel_url": (
            WEBSITE_URL
            + "/pricing.html"
        ),

        "metadata": metadata,

        "allow_promotion_codes": True,

        "billing_address_collection": "auto",
    }

    if request.email:

        params["customer_email"] = (
            str(request.email)
        )

    try:

        session = (
            stripe.checkout.Session.create(
                **params
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
    }


# ============================================================
# ACTIVATE
# ============================================================

@app.post("/v1/license/activate")
def activate_license(
    request: ActivateRequest,
    db: Session = Depends(get_db),
):

    if request.product != PRODUCT_CODE:

        raise HTTPException(
            status_code=400,
            detail="Incorrect product.",
        )

    license_obj = find_license(
        db,
        request.license_key,
    )

    if not license_obj:

        raise HTTPException(
            status_code=404,
            detail="Invalid license key.",
        )

    status = effective_status(
        license_obj
    )

    if status != "ACTIVE":

        raise HTTPException(
            status_code=403,
            detail=f"License is {status.lower()}.",
        )

    existing = (
        db.query(Activation)
        .filter(
            Activation.license_id
            == license_obj.id,

            Activation.installation_id
            == request.installation_id,

            Activation.deactivated_at
            == None,
        )
        .first()
    )

    if existing:

        existing.last_seen = datetime.now(
            timezone.utc
        )

        db.commit()

        return {
            "valid": True,
            "status": "ACTIVE",
            "plan": license_obj.plan,
            "expires_at": license_obj.expires_at.isoformat(),
            "activation_id": existing.id,
            "max_activations": license_obj.max_activations,
        }

    active_count = (
        db.query(Activation)
        .filter(
            Activation.license_id
            == license_obj.id,

            Activation.deactivated_at
            == None,
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

        installation_id=(
            request.installation_id
        ),

        machine_hash=(
            request.machine_hash
        ),

        activated_at=datetime.now(
            timezone.utc
        ),

        last_seen=datetime.now(
            timezone.utc
        ),
    )

    db.add(
        activation
    )

    db.commit()

    db.refresh(
        activation
    )

    return {

        "valid": True,

        "status": "ACTIVE",

        "plan": license_obj.plan,

        "expires_at": (
            license_obj
            .expires_at
            .isoformat()
        ),

        "activation_id": (
            activation.id
        ),

        "max_activations": (
            license_obj.max_activations
        ),
    }


# ============================================================
# VALIDATE
# ============================================================

@app.post("/v1/license/validate")
def validate_license(
    request: ValidateRequest,
    db: Session = Depends(get_db),
):

    if request.product != PRODUCT_CODE:

        raise HTTPException(
            status_code=400,
            detail="Incorrect product.",
        )

    license_obj = find_license(
        db,
        request.license_key,
    )

    if not license_obj:

        raise HTTPException(
            status_code=404,
            detail="Invalid license.",
        )

    status = effective_status(
        license_obj
    )

    activation = (
        db.query(Activation)
        .filter(
            Activation.license_id
            == license_obj.id,

            Activation.installation_id
            == request.installation_id,

            Activation.deactivated_at
            == None,
        )
        .first()
    )

    if not activation:

        raise HTTPException(
            status_code=403,
            detail="This computer is not activated.",
        )

    activation.last_seen = datetime.now(
        timezone.utc
    )

    db.commit()

    return {

        "valid": status == "ACTIVE",

        "status": status,

        "plan": license_obj.plan,

        "expires_at": (
            license_obj
            .expires_at
            .isoformat()
        ),

        "max_activations": (
            license_obj.max_activations
        ),

    }


# ============================================================
# DEACTIVATE
# ============================================================

@app.post("/v1/license/deactivate")
def deactivate_license(
    request: DeactivateRequest,
    db: Session = Depends(get_db),
):

    license_obj = find_license(
        db,
        request.license_key,
    )

    if not license_obj:

        raise HTTPException(
            status_code=404,
            detail="Invalid license.",
        )

    activation = (
        db.query(Activation)
        .filter(
            Activation.license_id
            == license_obj.id,

            Activation.installation_id
            == request.installation_id,

            Activation.deactivated_at
            == None,
        )
        .first()
    )

    if not activation:

        raise HTTPException(
            status_code=404,
            detail="Activation not found.",
        )

    activation.deactivated_at = (
        datetime.now(
            timezone.utc
        )
    )

    db.commit()

    return {
        "success": True,
    }


# ============================================================
# STRIPE WEBHOOK
# ============================================================

@app.post("/v1/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):

    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    if not signature:

        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature.",
        )

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload.",
        )

    except stripe.error.SignatureVerificationError:

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature.",
        )

    event_id = event["id"]

    existing = (
        db.query(StripeEvent)
        .filter(
            StripeEvent.stripe_event_id
            == event_id
        )
        .first()
    )

    if existing:

        return {
            "received": True,
            "duplicate": True,
        }

    event_record = StripeEvent(

        stripe_event_id=event_id,

        event_type=event["type"],

        received_at=datetime.now(
            timezone.utc
        ),
    )

    db.add(
        event_record
    )

    event_type = event["type"]

    # --------------------------------------------------------
    # CHECKOUT COMPLETED
    # --------------------------------------------------------

    if event_type == "checkout.session.completed":

        session = event["data"]["object"]

        metadata = (
            session.get("metadata")
            or {}
        )

        product = metadata.get(
            "product"
        )

        plan = metadata.get(
            "plan"
        )

        if product == PRODUCT_CODE and plan in PLANS:

            customer_email = (
                session.get("customer_details", {})
                .get("email")
            )

            customer_id = (
                session.get("customer")
            )

            subscription_id = (
                session.get("subscription")
            )

            existing_license = None

            if subscription_id:

                existing_license = (
                    db.query(License)
                    .filter(
                        License.stripe_subscription_id
                        == subscription_id
                    )
                    .first()
                )

            if not existing_license:

                create_license(
                    db=db,
                    plan=plan,
                    email=customer_email,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    stripe_checkout_session_id=session["id"],
                )

    # --------------------------------------------------------
    # SUBSCRIPTION UPDATED
    # --------------------------------------------------------

    elif event_type == "customer.subscription.updated":

        subscription = (
            event["data"]["object"]
        )

        subscription_id = subscription["id"]

        license_obj = (
            db.query(License)
            .filter(
                License.stripe_subscription_id
                == subscription_id
            )
            .first()
        )

        if license_obj:

            stripe_status = (
                subscription.get("status")
            )

            if stripe_status in (
                "active",
                "trialing",
            ):

                if license_obj.status != "REVOKED":

                    license_obj.status = "ACTIVE"

            elif stripe_status in (
                "past_due",
                "unpaid",
            ):

                license_obj.status = "PAST_DUE"

    # --------------------------------------------------------
    # SUBSCRIPTION DELETED
    # --------------------------------------------------------

    elif event_type == "customer.subscription.deleted":

        subscription = (
            event["data"]["object"]
        )

        subscription_id = subscription["id"]

        license_obj = (
            db.query(License)
            .filter(
                License.stripe_subscription_id
                == subscription_id
            )
            .first()
        )

        if license_obj:

            # Do not immediately revoke already-paid time.
            # Expiration remains the authoritative cutoff.
            license_obj.status = "ACTIVE"

    db.commit()

    return {
        "received": True,
    }


# ============================================================
# ADMIN AUTH
# ============================================================

def verify_admin(
    authorization: Optional[str]
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required.",
        )

    if not authorization.startswith(
        "Basic "
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication.",
        )

    import base64

    try:

        decoded = base64.b64decode(
            authorization[6:]
        ).decode()

        username, password = (
            decoded.split(":", 1)
        )

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication.",
        )

    if (
        username != ADMIN_USERNAME
        or password != ADMIN_PASSWORD
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials.",
        )


# ============================================================
# ADMIN: CREATE LICENSE
# ============================================================

class AdminCreateLicense(BaseModel):

    plan: str

    email: Optional[EmailStr] = None


@app.post("/v1/admin/licenses")
def admin_create_license(
    request: AdminCreateLicense,
    authorization: Optional[str] = Header(
        default=None
    ),
    db: Session = Depends(get_db),
):

    verify_admin(
        authorization
    )

    plan = request.plan.lower()

    if plan not in PLANS:

        raise HTTPException(
            status_code=400,
            detail="Invalid plan.",
        )

    key, license_obj = create_license(
        db=db,
        plan=plan,
        email=(
            str(request.email)
            if request.email
            else None
        ),
    )

    return {

        "license_key": key,

        "plan": plan,

        "expires_at": (
            license_obj
            .expires_at
            .isoformat()
        ),

        "max_activations": (
            license_obj
            .max_activations
        ),
    }


# ============================================================
# ADMIN: LIST LICENSES
# ============================================================

@app.get("/v1/admin/licenses")
def admin_list_licenses(
    authorization: Optional[str] = Header(
        default=None
    ),
    db: Session = Depends(get_db),
):

    verify_admin(
        authorization
    )

    licenses = (
        db.query(License)
        .order_by(
            License.id.desc()
        )
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
                [
                    a
                    for a in x.activations
                    if a.deactivated_at is None
                ]
            ),
        }

        for x in licenses

    ]


# ============================================================
# ADMIN: REVOKE
# ============================================================

@app.post(
    "/v1/admin/licenses/{license_id}/revoke"
)
def admin_revoke(
    license_id: int,
    authorization: Optional[str] = Header(
        default=None
    ),
    db: Session = Depends(get_db),
):

    verify_admin(
        authorization
    )

    license_obj = (
        db.query(License)
        .filter(
            License.id == license_id
        )
        .first()
    )

    if not license_obj:

        raise HTTPException(
            status_code=404,
            detail="License not found.",
        )

    license_obj.status = "REVOKED"

    db.commit()

    return {
        "success": True,
    }


# ============================================================
# ADMIN: RESET ACTIVATIONS
# ============================================================

@app.post(
    "/v1/admin/licenses/{license_id}/reset-activations"
)
def admin_reset_activations(
    license_id: int,
    authorization: Optional[str] = Header(
        default=None
    ),
    db: Session = Depends(get_db),
):

    verify_admin(
        authorization
    )

    license_obj = (
        db.query(License)
        .filter(
            License.id == license_id
        )
        .first()
    )

    if not license_obj:

        raise HTTPException(
            status_code=404,
            detail="License not found.",
        )

    now = datetime.now(
        timezone.utc
    )

    for activation in license_obj.activations:

        if activation.deactivated_at is None:

            activation.deactivated_at = now

    db.commit()

    return {
        "success": True,
    }
