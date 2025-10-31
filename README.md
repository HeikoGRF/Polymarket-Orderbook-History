# Polymarket Orderbook Listener

A Go WebSocket client for listening to real-time orderbook updates from Polymarket's CLOB (Central Limit Order Book).

## Features

- 🔌 WebSocket connection to Polymarket's market channel
- 📊 Real-time orderbook snapshot updates
- 💹 Price change notifications
- 📈 Trade execution events
- 🔄 Tick size change notifications
- 💓 Automatic PING/PONG keep-alive mechanism
- 🛡️ Graceful shutdown with Ctrl+C
- 💾 **Automatic JSON file storage** - All data saved to files
- 📁 Separate files for each message type (JSONL format)
- ₿ **Bitcoin price tracking** - Real-time BTC price added to orderbook snapshots
- 🕐 **Hourly BTC snapshots** - Tracks BTC price at start of each hour

## Prerequisites

- Go 1.21 or higher
- Internet connection

## Installation

1. Clone or navigate to this directory:
```bash
cd /Users/heikograef/development/ALL_POLY/orderbook_listener
```

2. Install dependencies:
```bash
go mod download
```

## Usage

### Basic Usage

Run the client with the default example asset ID:

```bash
go run polymarket_client.go
```

### Custom Asset IDs

To track different markets, modify the `assetIDs` slice in the `main()` function in `polymarket_client.go`:

```go
assetIDs := []string{
    "YOUR_ASSET_ID_1",
    "YOUR_ASSET_ID_2",
    // Add more asset IDs as needed
}
```

### Finding Asset IDs

You can find asset IDs by:
1. Visiting the Polymarket website
2. Using the Polymarket API to query available markets
3. Checking the Polymarket documentation at https://docs.polymarket.com

## Message Types

The client handles four types of WebSocket messages:

### 1. Book Message (Orderbook Snapshot)
Received when:
- First subscribing to a market
- After a trade that affects the orderbook

Shows the current state of bids and asks with price levels and sizes.

### 2. Price Change Message
Received when:
- A new order is placed
- An order is cancelled

Shows which price levels have changed and the new sizes.

### 3. Tick Size Change Message
Received when:
- The minimum tick size changes (when price > 0.96 or price < 0.04)

### 4. Last Trade Price Message
Received when:
- A maker and taker order is matched, creating a trade

Shows the execution price, size, and side of the trade.

## Configuration

### WebSocket URL
The client connects to: `wss://ws-subscriptions-clob.polymarket.com/ws/market`

### Ping Interval
The client sends PING messages every 10 seconds to keep the connection alive. You can modify this in the code:

```go
const PingInterval = 10 * time.Second
```

## Code Structure

- `PolymarketClient`: Main client struct managing the WebSocket connection
- `OrderSummary`: Represents a single price level (price + size)
- `BookMessage`: Full orderbook snapshot
- `PriceChangeMessage`: Price level updates
- `TickSizeChangeMessage`: Tick size changes
- `LastTradePriceMessage`: Trade execution events

## Example Output

```
2025/10/31 10:00:00 Connecting to wss://ws-subscriptions-clob.polymarket.com/ws/market
2025/10/31 10:00:00 Connected successfully
2025/10/31 10:00:00 Subscribing to asset IDs: [109681959945973300464568698402968596289258214226684818748321941747028805721376]
2025/10/31 10:00:00 Subscription message sent
2025/10/31 10:00:00 Listening for orderbook updates... Press Ctrl+C to exit
========== ORDERBOOK SNAPSHOT ==========
Asset ID: 109681959945973300464568698402968596289258214226684818748321941747028805721376
Market: 0xbd31dc8a20211944f6b70f31557f1001557b59905b7738480ca09bd4532f84af
Timestamp: 1698748800000

Bids (Buy Orders):
  Price: 0.48, Size: 30
  Price: 0.49, Size: 20
  Price: 0.50, Size: 15

Asks (Sell Orders):
  Price: 0.52, Size: 25
  Price: 0.53, Size: 60
  Price: 0.54, Size: 10
=======================================
```

## Data Storage

All incoming market data is automatically saved to JSON files in the `data/` directory:

- **`orderbook_snapshots.json`** - Full orderbook snapshots with all bids/asks
// price_changes.json storage disabled by request
- **`trades.json`** - Trade execution events
- **`tick_size_changes.json`** - Tick size change events

Files use **JSONL format** (one JSON object per line), making them easy to process line-by-line.

### Reading the Data

Use the included Python script to view and analyze the data:

```bash
# Show statistics about stored data
python read_data.py --stats

# Show last 5 orderbook snapshots
python read_data.py --snapshots --limit 5

# Show last 10 trades with volume analysis
python read_data.py --trades --limit 10

# Show all price changes
python read_data.py --price-changes

# Show everything
python read_data.py --all
```

See [`DATA_STORAGE.md`](DATA_STORAGE.md) for detailed format documentation and examples in Python, Go, and JavaScript.

## Bitcoin Price Tracking

The client automatically tracks Bitcoin prices and adds them to each orderbook snapshot:

- **`btc_price_current`**: Current Bitcoin price (real-time via Polymarket RTDS, acts as the "Close")
- **`btc_price_hourly_open`**: Official open price from **Binance REST API** - guaranteed accurate!

### Why Binance API for Hourly Open?

To ensure **100% accuracy** for market resolution, we fetch the hourly open price directly from [Binance's REST API](https://api.binance.com/api/v3/klines) instead of relying on real-time streams. This guarantees `btc_price_hourly_open` **exactly matches** the official Binance 1H candle open price that Polymarket uses for resolution.

**Resolution Logic:**
> *Resolves to "Up" if close ≥ open, otherwise "Down"*

This runs with **zero performance impact** - the Binance API is called only once per hour (when a new hour starts), and real-time prices come from [Polymarket's RTDS](https://docs.polymarket.com/developers/RTDS/RTDS-crypto-prices) in a separate goroutine.

**Example orderbook entry with BTC prices:**
```json
{
  "event_type": "book",
  "asset_id": "...",
  "timestamp": "1761916143357",
  "btc_price_current": 109780.62,
  "btc_price_hourly_open": 109763.54,
  "bids": [...],
  "asks": [...]
}
```

**Determining Market Resolution:**
- If `btc_price_current >= btc_price_hourly_open` → Market resolves **"Up"** 📈
- If `btc_price_current < btc_price_hourly_open` → Market resolves **"Down"** 📉

This allows you to correlate orderbook changes with Bitcoin price movements and predict market resolution!

## Stopping the Client

Press `Ctrl+C` to gracefully shut down the client. It will:
1. Send a close message to the server
2. Close the WebSocket connection
3. Close all data files
4. Exit cleanly

## Authentication (User Channel)

This client currently implements the public `market` channel, which doesn't require authentication. If you need to implement the `user` channel for private updates, you'll need to:

1. Obtain API credentials (apiKey, secret, passphrase) from Polymarket
2. Modify the subscribe message to include authentication
3. Change the channel type to `user`

See the [Polymarket WebSocket Authentication documentation](https://docs.polymarket.com/developers/CLOB/websocket/wss-auth) for more details.

## References

- [Polymarket WebSocket Quickstart](https://docs.polymarket.com/quickstart/websocket/WSS-Quickstart)
- [Polymarket WebSocket Authentication](https://docs.polymarket.com/developers/CLOB/websocket/wss-auth)
- [Polymarket Market Channel](https://docs.polymarket.com/developers/CLOB/websocket/market-channel)

## License

This is example code for educational purposes. Use at your own risk.

# Polymarket-Orderbook-History
