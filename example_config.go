package main

// This file contains example configurations and helper functions
// for customizing your Polymarket orderbook listener

// Example asset IDs for different markets
// Replace these with actual asset IDs from Polymarket

var (
	// Example from Polymarket documentation
	ExampleAssetID = "109681959945973300464568698402968596289258214226684818748321941747028805721376"
	
	// Add your own asset IDs here
	// You can find these by:
	// 1. Visiting a market on polymarket.com
	// 2. Using the Polymarket API
	// 3. Checking the Gamma markets endpoint
)

// PresetConfigurations contains some common monitoring setups
var PresetConfigurations = map[string][]string{
	"single_market": {
		ExampleAssetID,
	},
	
	"multiple_markets": {
		// Add multiple asset IDs to monitor several markets at once
		ExampleAssetID,
		// "ANOTHER_ASSET_ID",
		// "YET_ANOTHER_ASSET_ID",
	},
}

// GetAssetIDsFromPreset returns asset IDs for a given preset configuration
func GetAssetIDsFromPreset(presetName string) []string {
	if assetIDs, ok := PresetConfigurations[presetName]; ok {
		return assetIDs
	}
	return []string{ExampleAssetID} // Default fallback
}

// Example usage in main.go:
// 
// func main() {
//     // Use a preset configuration
//     assetIDs := GetAssetIDsFromPreset("single_market")
//     
//     // Or define custom asset IDs
//     // assetIDs := []string{
//     //     "YOUR_ASSET_ID_HERE",
//     // }
//     
//     client := NewPolymarketClient(assetIDs, nil)
//     // ... rest of the code
// }

