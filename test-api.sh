#!/bin/bash

echo "=== Testing TeamFlow API ==="
echo ""

BACKEND_URL="http://192.168.0.3:8180"

echo "1. Testing health endpoint..."
curl -s "${BACKEND_URL}/health"
echo ""
echo ""

echo "2. Testing bot-info endpoint..."
curl -s "${BACKEND_URL}/api/bot-info"
echo ""
echo ""

echo "3. Testing login endpoint..."
curl -X POST "${BACKEND_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"teamflow"}' \
  -v
echo ""
