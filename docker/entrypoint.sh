#!/bin/bash
set -e

# ==================== 环境配置检查 ====================

if [ ! -f "/app/env.yaml" ]; then
    echo "错误: 未找到 /app/env.yaml"
    echo "请确保已挂载 env.yaml 到容器内 /app/env.yaml"
    echo "参考 env.example.yaml 创建配置文件"
    exit 1
fi
echo "检测到环境配置文件 env.yaml"

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

# ==================== 迁移检查 ====================

echo "检查数据迁移..."
python /app/migrate.py

# ==================== 启动 Fava ====================

echo "启动 Fava..."
fava /app/data/main.bean --host 127.0.0.1 --port 5000 --prefix /fava &
echo "Fava 已启动 (127.0.0.1:5000, prefix=/fava)"

# 等待 Fava 就绪
echo "等待 Fava 就绪..."
for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:5000/fava/ > /dev/null 2>&1; then
        echo "Fava 已就绪"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "警告: Fava 未在 30 秒内就绪，继续启动 Web 服务"
    fi
    sleep 1
done

# ==================== 启动 Uvicorn ====================

echo "启动 IhopeCash Web 服务..."
echo "  HTTPS: https://localhost"
echo "  Fava:  https://localhost/fava/"
echo ""

exec uvicorn web.app:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 1
