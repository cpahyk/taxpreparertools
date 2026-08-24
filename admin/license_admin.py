import base64
import os
import sys

import requests


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000",
).rstrip("/")

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin",
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
)


def auth_headers():
    if not ADMIN_PASSWORD:
        raise RuntimeError(
            "ADMIN_PASSWORD is not set."
        )

    credentials = (
        f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}"
    )

    encoded = base64.b64encode(
        credentials.encode("utf-8")
    ).decode("ascii")

    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }


def request_json(
    method,
    path,
    **kwargs,
):
    response = requests.request(
        method,
        API_BASE_URL + path,
        headers=auth_headers(),
        timeout=30,
        **kwargs,
    )

    if response.status_code >= 400:
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"{response.status_code}: {detail}"
        )

    return response.json()


def create_license():
    print()
    plan = input(
        "Plan (monthly/yearly/pro): "
    ).strip().lower()

    if plan not in {
        "monthly",
        "yearly",
        "pro",
    }:
        print("Invalid plan.")
        return

    email = input(
        "Customer email (optional): "
    ).strip()

    data = request_json(
        "POST",
        "/v1/admin/licenses",
        json={
            "plan": plan,
            "email": email or None,
        },
    )

    print()
    print("==============================")
    print("LICENSE CREATED")
    print("==============================")
    print(
        "License:",
        data["license_key"],
    )
    print(
        "Plan:",
        data["plan"],
    )
    print(
        "Expires:",
        data["expires_at"],
    )
    print(
        "Max activations:",
        data["max_activations"],
    )
    print("==============================")


def list_licenses():
    data = request_json(
        "GET",
        "/v1/admin/licenses",
    )

    print()

    if not data:
        print("No licenses found.")
        return

    for license_item in data:
        print(
            f'ID: {license_item["id"]} | '
            f'Prefix: {license_item["prefix"]} | '
            f'Plan: {license_item["plan"]} | '
            f'Status: {license_item["status"]} | '
            f'Email: {license_item["email"]} | '
            f'Activations: '
            f'{license_item["activations"]}/'
            f'{license_item["max_activations"]} | '
            f'Expires: '
            f'{license_item["expires_at"]}'
        )


def revoke_license():
    license_id = input(
        "License ID to revoke: "
    ).strip()

    if not license_id.isdigit():
        print("Invalid license ID.")
        return

    data = request_json(
        "POST",
        f"/v1/admin/licenses/{license_id}/revoke",
    )

    print("Result:", data)


def reset_activations():
    license_id = input(
        "License ID: "
    ).strip()

    if not license_id.isdigit():
        print("Invalid license ID.")
        return

    data = request_json(
        "POST",
        f"/v1/admin/licenses/"
        f"{license_id}/reset-activations",
    )

    print("Result:", data)


def main():
    print()
    print("================================")
    print("TaxPreparerTools License Admin")
    print("================================")
    print(
        "API:",
        API_BASE_URL,
    )

    while True:
        print()
        print("================================")
        print("1. Create license")
        print("2. List licenses")
        print("3. Revoke license")
        print("4. Reset activations")
        print("5. Exit")
        print("================================")

        choice = input(
            "Select: "
        ).strip()

        try:
            if choice == "1":
                create_license()

            elif choice == "2":
                list_licenses()

            elif choice == "3":
                revoke_license()

            elif choice == "4":
                reset_activations()

            elif choice == "5":
                print("Goodbye.")
                return

            else:
                print("Invalid selection.")

        except requests.exceptions.ConnectionError:
            print()
            print(
                "ERROR: Cannot connect to API:"
            )
            print(API_BASE_URL)

        except Exception as exc:
            print()
            print("ERROR:", exc)


if __name__ == "__main__":
    main()
