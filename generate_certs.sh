#!/bin/bash
set -e

CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

echo "Generating CA..."
openssl genrsa -out "$CERT_DIR/ca.key" 2048
openssl req -x509 -new -nodes -key "$CERT_DIR/ca.key" -sha256 -days 3650 -out "$CERT_DIR/ca.crt" -subj "/CN=SmartHomeCA"

echo "Generating Server Certificate..."
openssl genrsa -out "$CERT_DIR/server.key" 2048
openssl req -new -key "$CERT_DIR/server.key" -out "$CERT_DIR/server.csr" -subj "/CN=mosquitto"
openssl x509 -req -in "$CERT_DIR/server.csr" -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial -out "$CERT_DIR/server.crt" -days 3650 -sha256

echo "Generating Backend Certificate..."
openssl genrsa -out "$CERT_DIR/backend.key" 2048
openssl req -new -key "$CERT_DIR/backend.key" -out "$CERT_DIR/backend.csr" -subj "/CN=backend"
openssl x509 -req -in "$CERT_DIR/backend.csr" -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial -out "$CERT_DIR/backend.crt" -days 3650 -sha256

echo "Generating Gateway Certificate..."
openssl genrsa -out "$CERT_DIR/gateway.key" 2048
openssl req -new -key "$CERT_DIR/gateway.key" -out "$CERT_DIR/gateway.csr" -subj "/CN=gateway-001"
openssl x509 -req -in "$CERT_DIR/gateway.csr" -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial -out "$CERT_DIR/gateway.crt" -days 3650 -sha256

echo "Done. Certificates and keys generated in $CERT_DIR"
