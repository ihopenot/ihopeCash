#!/bin/bash
set -e

CERT_DIR="/app/certs"
CERT_FILE="$CERT_DIR/cert.pem"
KEY_FILE="$CERT_DIR/key.pem"

# ==================== SSL 证书 ====================

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "未检测到 SSL 证书，正在生成自签证书..."
    mkdir -p "$CERT_DIR"
    openssl req -x509 -nodes -days 365 \
        -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/CN=ihopecash/O=IhopeCash/C=CN" \
        2>/dev/null
    echo "自签证书已生成"
else
    echo "检测到 SSL 证书，使用外部证书"
fi

# ==================== 启动 Nginx ====================

echo "启动 Nginx..."
nginx
echo "Nginx 已启动"

# ==================== 启动 Fava ====================

echo "启动 Fava..."
fava /app/main.bean --host 127.0.0.1 --port 5000 --prefix /fava &
echo "Fava 已启动 (127.0.0.1:5000, prefix=/fava)"

# ==================== 启动 Uvicorn ====================

echo "启动 IhopeCash Web 服务..."
echo "  HTTPS: https://localhost"
echo "  Fava:  https://localhost/fava/"
echo ""

exec uvicorn web.app:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 1
