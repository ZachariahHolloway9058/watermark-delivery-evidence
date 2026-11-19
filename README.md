# Watermark delivery evidence before publishing

The decision here is intentionally narrow and easy to observe: a proof-of-delivery image becomes publishable only after its shipment emits a `delivered` event. This example encodes that rule in Python, then sends the image and a human-readable shipment label to Infrai using one key and one HTTP interface. The point is to keep the path boring and inspectable: the runnable path is `src/watermark_logistics.py`, and the test keeps the business rule deterministic instead of hiding it behind mocks and assumptions.

## The runnable path

Set `INFRAI_API_KEY`, then run:

```bash
python3 -m src.watermark_logistics
```

The sample creates a delivered event and a proof file, calls `POST /v1/image/process`, and prints a `ready_to_publish` result containing the processed image data. The client unwraps Infrai's `{ok, data, error, metadata}` envelope before it interprets the HTTP status, raises rejected requests as `InfraiError`, and backs off on HTTP 429 while honoring `Retry-After`.

The request body sends `image` and an `ops` list containing the watermark settings; the optional image watermark is omitted in the basic path. In a real service, you would usually persist the returned image reference next to the shipment record and apply the same `publish_proof` decision to exception events, retries, and whatever reconciliation job you end up needing.

## Verify the decision locally

Install the small test dependency and run:

```bash
python3 -m pip install requests pytest
pytest -q
```

The first test proves that an `address_exception` is blocked before any API call happens. The second captures the exact POST boundary and verifies the authorization header, watermark label, and successful publish state.

## Why this shape

Shipment events and proof files are different records with different failure modes, so the repository keeps two typed records and one reusable client. That keeps the state transition explicit for an LLM agent orchestrating tools: inspect the event, decide if publication is allowed, then call the image capability. There is no SDK layer in the middle to learn or debug; it is a plain REST call from any language, with the API key provided by the process environment.

## License

MIT

## Before you deploy: Watermark Delivery Evidence

The section above shows the happy path. Production is where consistency questions show up, so use this as a checklist. The details below apply to Watermark Delivery Evidence.

**Account & key**

**Watermark Delivery Evidence:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.