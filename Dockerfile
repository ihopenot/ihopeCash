FROM python:3.12-slim

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nginx \
        openssl \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m -u 1000 appuser

WORKDIR /app

# 先复制依赖文件，利用 Docker 层缓存
COPY requirements.txt ./
COPY web/requirements.txt ./web/requirements.txt
COPY china_bean_importers/ ./china_bean_importers/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r web/requirements.txt && \
    pip install --no-cache-dir -e china_bean_importers/ && \
    pip install --no-cache-dir fava

# 复制项目文件
COPY backend.py config.py beancount_config.py mail.py main.py migrate.py ./
COPY web/ ./web/
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 创建必要目录并设置权限
RUN mkdir -p /app/certs /app/data /app/rawdata /app/archive && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /var/log/nginx && \
    chown -R appuser:appuser /var/lib/nginx && \
    chown -R appuser:appuser /run

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 80 443

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/setup/status || exit 1

ENTRYPOINT ["/entrypoint.sh"]
