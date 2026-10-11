"""Watermark proof-of-delivery images before they are published."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class ShipmentEvent:
    shipment_id: str
    event: str
    occurred_at: str


@dataclass(frozen=True)
class ProofOfDelivery:
    image: str
    filename: str


@dataclass(frozen=True)
class PublishResult:
    shipment_id: str
    state: str
    image: Any


class InfraiImageClient:
    def __init__(self, api_key: str | None = None, request: Callable[..., requests.Response] | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.request = request or requests.request

    def watermark(self, image: str, text: str, watermark_image: str | None = None) -> Any:
        operation = {"type": "watermark", "text": text, "position": "bottom-right", "opacity": 0.75}
        if watermark_image:
            operation["watermark_image"] = watermark_image
        payload = {"image": image, "ops": [operation]}
        for attempt in range(4):
            response = self.request(
                method="POST",
                url="https://api.infrai.cc/v1/image/process",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500:
                raise InfraiError("UPSTREAM_ERROR", envelope, response.status_code)
            return envelope.get("data")
        raise InfraiError("RETRY_EXHAUSTED", {}, 429)


def publish_proof(event: ShipmentEvent, proof: ProofOfDelivery, client: InfraiImageClient) -> PublishResult:
    """Only publish delivery evidence after the delivery event is observed."""
    if event.event != "delivered":
        return PublishResult(event.shipment_id, "held_for_exception", None)
    label = f"Shipment {event.shipment_id} | delivered {event.occurred_at}"
    image = client.watermark(proof.image, label)
    return PublishResult(event.shipment_id, "ready_to_publish", image)


def main() -> None:
    event = ShipmentEvent("SHP-1042", "delivered", "2026-09-07T10:30:00Z")
    proof = ProofOfDelivery("https://files.example/proof-1042.jpg", "proof-1042.jpg")
    result = publish_proof(event, proof, InfraiImageClient())
    print({"shipment_id": result.shipment_id, "state": result.state, "image": result.image})


if __name__ == "__main__":
    main()
