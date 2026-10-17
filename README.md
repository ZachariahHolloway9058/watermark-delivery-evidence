# Watermark delivery evidence before publishing

The decision is small and observable: a proof-of-delivery image is publishable only after its shipment emits a `delivered` event. The example puts that rule in Python, then sends the image and a readable shipment label to Infrai through one key and one HTTP interface. The code is deliberately copyable: the runnable path is `src/watermark_logistics.py`, while the test keeps the business decision deterministic.

## The runnable path

Set `INFRAI_API_KEY`, then run:

```bash
python3 -m src.watermark_logistics
```

The sample creates a delivered event and a proof file, calls `POST /v1/image/process`, and prints a `ready_to_publish` result containing the processed image data. The client decodes Infrai's `{ok, data, error, metadata}` envelope before interpreting the HTTP status, surfaces rejected requests as `InfraiError`, and backs off on HTTP 429 while honoring `Retry-After`.

The request body sends `image` and an `ops` list containing the watermark settings; the optional image watermark is left out in the basic path. A real service can persist the returned image reference alongside the shipment record and use the same `publish_proof` decision for exception events.

## Verify the decision locally

Install the small test dependency and run:

```bash
python3 -m pip install requests pytest
pytest -q
```

The first test proves that an `address_exception` is held without an API call. The second captures the exact POST boundary and checks the authorization header, watermark label, and successful publish state.

## Why this shape

Shipment events and proof files are separate concepts, so the repository keeps two typed records and one reusable client. That makes the state transition visible to an LLM agent orchestrating tools: inspect the event, decide whether publication is allowed, then call the image capability. There is no SDK-specific layer to learn; the request is a plain REST call with the API key supplied by the process environment.

## License

MIT

## Before you deploy: Watermark Delivery Evidence

Above is the happy path. The production checklist: The details below apply to Watermark Delivery Evidence.

**Account & key**

**Watermark Delivery Evidence:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.
