#!/usr/bin/env python3
"""
Simple script to read and analyze Polymarket orderbook data from JSON files.
"""

import json
import os
from datetime import datetime
from collections import defaultdict


def format_timestamp(ts_str):
    """Convert millisecond timestamp string to readable format."""
    try:
        ts = int(ts_str) / 1000.0  # Convert from ms to seconds
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts_str


def read_orderbook_snapshots(filepath='data/orderbook_snapshots.json', limit=None):
    """Read and display orderbook snapshots."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    print("\n" + "="*70)
    print("ORDERBOOK SNAPSHOTS")
    print("="*70)
    
    count = 0
    with open(filepath, 'r') as f:
        for line in f:
            if limit and count >= limit:
                break
            
            snapshot = json.loads(line)
            
            print(f"\nSnapshot #{count + 1}")
            print(f"Time: {format_timestamp(snapshot['timestamp'])}")
            print(f"Asset ID: {snapshot['asset_id'][:20]}...")
            print(f"Market: {snapshot['market']}")
            
            # Show BTC prices if available
            if 'btc_price_current' in snapshot and snapshot['btc_price_current'] > 0:
                current = snapshot['btc_price_current']
                hourly_open = snapshot.get('btc_price_hourly_open', snapshot.get('btc_price_hourly', 0))
                
                if hourly_open > 0:
                    movement = "UP 📈" if current >= hourly_open else "DOWN 📉"
                    change = current - hourly_open
                    change_pct = (change / hourly_open) * 100
                    print(f"BTC 1H Candle: Open=${hourly_open:,.2f} Current=${current:,.2f} ({change:+.2f} / {change_pct:+.2f}%) {movement}")
                else:
                    print(f"BTC Price: ${current:,.2f}")
            
            if snapshot['bids']:
                print(f"\nTop 5 Bids:")
                for i, bid in enumerate(snapshot['bids'][:5]):
                    print(f"  {i+1}. Price: {bid['price']:>6s}  Size: {bid['size']}")
            
            if snapshot['asks']:
                print(f"\nTop 5 Asks:")
                for i, ask in enumerate(snapshot['asks'][:5]):
                    print(f"  {i+1}. Price: {ask['price']:>6s}  Size: {ask['size']}")
            
            count += 1
    
    print(f"\nTotal snapshots: {count}")


def read_price_changes(filepath='data/price_changes.json', limit=None):
    """Deprecated: price change storage disabled."""
    print("price_changes.json storage is disabled.")


def read_trades(filepath='data/trades.json', limit=None):
    """Read and display trades."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    print("\n" + "="*70)
    print("TRADES")
    print("="*70)
    
    count = 0
    total_volume = 0.0
    side_counts = defaultdict(int)
    
    with open(filepath, 'r') as f:
        for line in f:
            if limit and count >= limit:
                break
            
            trade = json.loads(line)
            
            print(f"\nTrade #{count + 1}")
            print(f"Time: {format_timestamp(trade['timestamp'])}")
            print(f"Asset ID: {trade['asset_id'][:20]}...")
            print(f"Side: {trade['side']:>4s}  Price: {trade['price']:>6s}  Size: {trade['size']}")
            print(f"Fee Rate: {trade['fee_rate_bps']} bps ({float(trade['fee_rate_bps'])/100}%)")
            
            # Calculate notional value
            notional = float(trade['price']) * float(trade['size'])
            print(f"Notional Value: ${notional:.2f}")
            
            count += 1
            total_volume += notional
            side_counts[trade['side']] += 1
    
    print(f"\n{'='*70}")
    print(f"Total trades: {count}")
    print(f"Total volume: ${total_volume:.2f}")
    if side_counts:
        print(f"Buy trades: {side_counts['BUY']}")
        print(f"Sell trades: {side_counts['SELL']}")


def read_tick_size_changes(filepath='data/tick_size_changes.json'):
    """Read and display tick size changes."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    print("\n" + "="*70)
    print("TICK SIZE CHANGES")
    print("="*70)
    
    count = 0
    with open(filepath, 'r') as f:
        for line in f:
            change = json.loads(line)
            
            print(f"\nChange #{count + 1}")
            print(f"Time: {format_timestamp(change['timestamp'])}")
            print(f"Asset ID: {change['asset_id'][:20]}...")
            print(f"Market: {change['market']}")
            print(f"Old Tick Size: {change['old_tick_size']} -> New Tick Size: {change['new_tick_size']}")
            
            count += 1
    
    print(f"\nTotal tick size changes: {count}")


def get_statistics(data_dir='data'):
    """Display statistics about the stored data."""
    print("\n" + "="*70)
    print("DATA STATISTICS")
    print("="*70)
    
    files = {
        'Orderbook Snapshots': 'orderbook_snapshots.json',
        'Trades': 'trades.json',
        'Tick Size Changes': 'tick_size_changes.json',
    }
    
    for name, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            # Count lines
            with open(filepath, 'r') as f:
                line_count = sum(1 for _ in f)
            
            # Get file size
            size_bytes = os.path.getsize(filepath)
            size_mb = size_bytes / (1024 * 1024)
            
            print(f"\n{name}:")
            print(f"  File: {filepath}")
            print(f"  Messages: {line_count}")
            print(f"  Size: {size_mb:.2f} MB")
        else:
            print(f"\n{name}: No data yet")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Read and analyze Polymarket orderbook data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show statistics about stored data
  python read_data.py --stats
  
  # Show last 5 orderbook snapshots
  python read_data.py --snapshots --limit 5
  
  # Show last 10 trades
  python read_data.py --trades --limit 10
  
  # Show all price changes
  python read_data.py --price-changes
  
  # Show everything
  python read_data.py --all
        """
    )
    
    parser.add_argument('--stats', action='store_true', help='Show data statistics')
    parser.add_argument('--snapshots', action='store_true', help='Show orderbook snapshots')
    parser.add_argument('--price-changes', action='store_true', help='(disabled)')
    parser.add_argument('--trades', action='store_true', help='Show trades')
    parser.add_argument('--tick-changes', action='store_true', help='Show tick size changes')
    parser.add_argument('--all', action='store_true', help='Show all data')
    parser.add_argument('--limit', type=int, help='Limit number of records to display')
    parser.add_argument('--data-dir', default='data', help='Data directory (default: data)')
    
    args = parser.parse_args()
    
    # If no specific flag is set, show stats
    if not any([args.stats, args.snapshots, args.trades, args.tick_changes, args.all]):
        args.stats = True
    
    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory '{args.data_dir}' does not exist.")
        print("Run the Go client first to generate data.")
        return
    
    # Display requested data
    if args.stats or args.all:
        get_statistics(args.data_dir)
    
    if args.snapshots or args.all:
        read_orderbook_snapshots(
            f'{args.data_dir}/orderbook_snapshots.json', 
            args.limit
        )
    
    if args.price_changes:
        read_price_changes(
            f'{args.data_dir}/price_changes.json',
            args.limit
        )
    
    if args.trades or args.all:
        read_trades(
            f'{args.data_dir}/trades.json',
            args.limit
        )
    
    if args.tick_changes or args.all:
        read_tick_size_changes(
            f'{args.data_dir}/tick_size_changes.json'
        )


if __name__ == '__main__':
    main()

