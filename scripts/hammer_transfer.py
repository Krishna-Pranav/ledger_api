"""Fires 50 concurrent ₹10 transfers against a single ₹100 account to expose race conditions."""
import asyncio
import uuid

import httpx

BASE_URL = "http://localhost:8000"
NUM_TRANSFERS = 50
TRANSFER_AMOUNT = 10


async def register_and_login(client: httpx.AsyncClient) -> tuple[int, str]:
    email = f"hammer_{uuid.uuid4().hex[:8]}@test.com"
    password = "password123"

    resp = await client.post("/users", json={"email": email, "password": password})
    resp.raise_for_status()
    user_id = resp.json()["id"]

    resp = await client.post("/auth/login", json={"email": email, "password": password})
    resp.raise_for_status()
    token = resp.json()["access_token"]

    return user_id, token


async def create_account(client: httpx.AsyncClient, token: str, owner_name: str, balance: float) -> int:
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        "/accounts",
        json={"owner_name": owner_name, "currency": "INR"},
        headers=headers,
    )
    resp.raise_for_status()
    account_id = resp.json()["id"]

    if balance:
        resp = await client.patch(f"/accounts/{account_id}", json={"balance": balance}, headers=headers)
        resp.raise_for_status()

    return account_id


async def get_balance(client: httpx.AsyncClient, token: str, account_id: int) -> float:
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get(f"/accounts/{account_id}", headers=headers)
    resp.raise_for_status()
    return float(resp.json()["balance"])


async def fire_transfer(client: httpx.AsyncClient, token: str, from_id: int, to_id: int, idempotency_key: str) -> httpx.Response:
    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": idempotency_key}
    return await client.post(
        "/transfers",
        params={"from_account": from_id, "to_account": to_id, "amount": TRANSFER_AMOUNT},
        headers=headers,
    )


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        user_id, token = await register_and_login(client)
        suffix = uuid.uuid4().hex[:8]
        from_id = await create_account(client, token, f"hammer_from_{suffix}", 100)
        to_id = await create_account(client, token, f"hammer_to_{suffix}", 0)

        idempotency_key = str(uuid.uuid4())
        results = await asyncio.gather(
            *(fire_transfer(client, token, from_id, to_id, idempotency_key) for _ in range(NUM_TRANSFERS)),
            return_exceptions=True,
        )

        succeeded = sum(1 for r in results if isinstance(r, httpx.Response) and r.status_code == 200)
        failed = NUM_TRANSFERS - succeeded
        print(f"succeeded={succeeded} failed={failed}")

        bodies = [r.json() for r in results if isinstance(r, httpx.Response) and r.status_code == 200]
        transfer_ids = {b["id"] for b in bodies}
        print(f"distinct transfer ids returned: {transfer_ids}")

        final_from_balance = await get_balance(client, token, from_id)
        final_to_balance = await get_balance(client, token, to_id)
        print(f"final from-account balance: {final_from_balance}")
        print(f"final to-account balance:   {final_to_balance}")

        assert succeeded == NUM_TRANSFERS, f"expected all {NUM_TRANSFERS} requests to return 200, got {succeeded}"
        assert len(transfer_ids) == 1, f"expected exactly one transfer id, got {transfer_ids}"
        assert final_from_balance == 100 - TRANSFER_AMOUNT, "money moved more than once despite same idempotency key"
        assert final_to_balance == TRANSFER_AMOUNT, "money moved more than once despite same idempotency key"
        print("idempotency check passed: only one transfer was actually applied")


if __name__ == "__main__":
    asyncio.run(main())
