# Setup

```
pip install -r requirements.txt

ipfs init
ipfs daemon

python <script>
```

Start meca_executor outside this container too.

# Usage

To start mock actor: `python mock_<actor>.py`

To start tower server: `uvicorn tower_server:app --port <port>`
- Add `--ws-ping-timeout <seconds>` to increase the timeout for websocket pings.

