#!/bin/bash
cd "/Users/brandonin/IMEI-ASN-Match"

# Update all repo names
find . -type f \( -name "*.md" -o -name "*.txt" \) -exec sed -i '' 's/wrma-inbound-processor/imei-asn-match/g' {} +

# Update all product names
find . -type f \( -name "*.md" -o -name "*.txt" \) -exec sed -i '' 's/WRMA Inbound Processor/IMEI\/ASN Match/g' {} +

echo "✅ All files updated!"
