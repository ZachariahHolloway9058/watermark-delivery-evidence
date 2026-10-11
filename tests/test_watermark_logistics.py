import json

from src.watermark_logistics import (
    InfraiImageClient,
    ProofOfDelivery,
    ShipmentEvent,
    publish_proof,
)


class FakeResponse:
    status_code = 200
    headers = {}

    def json(self):
        return {"ok": True, "data": {"id": "processed-1"}, "error": None, "metadata": {}}


def test_exception_event_is_held_without_api_call():
    called = []
    client = InfraiImageClient("test-key", request=lambda **kwargs: called.append(kwargs))
    result = publish_proof(
        ShipmentEvent("SHP-1", "address_exception", "2026-09-07T10:30:00Z"),
        ProofOfDelivery("img", "proof.jpg"),
        client,
    )
    assert result.state == "held_for_exception"
    assert called == []


def test_delivery_sends_watermark_request():
    calls = []

    def request(**kwargs):
        calls.append(kwargs)
        return FakeResponse()

    result = publish_proof(
        ShipmentEvent("SHP-2", "delivered", "2026-09-07T10:30:00Z"),
        ProofOfDelivery("img", "proof.jpg"),
        InfraiImageClient("test-key", request=request),
    )
    assert result.state == "ready_to_publish"
    assert calls[0]["method"] == "POST"
    assert set(calls[0]["json"]) == {"image", "ops"}
    assert calls[0]["json"]["image"] == "img"
    assert calls[0]["json"]["ops"] == [{
        "type": "watermark",
        "text": "Shipment SHP-2 | delivered 2026-09-07T10:30:00Z",
        "position": "bottom-right",
        "opacity": 0.75,
    }]
    assert calls[0]["headers"]["Authorization"] == "Bearer test-key"
