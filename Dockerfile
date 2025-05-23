FROM python:3.12.7-alpine AS builder
WORKDIR /builder

RUN apk update && \
    apk add --no-cache \
    build-base \
    linux-headers

# 安装构建依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --upgrade pip && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn Cython setuptools

COPY setup.py setup.py
COPY app ./app

RUN python setup.py

RUN apk del build-base linux-headers && \
    find app -type f \( -name "*.py" ! -name "main.py" ! -name "__init__.py" -o -name "*.c" \) -delete

FROM python:3.12.7-alpine

ENV TZ=Asia/Shanghai
VOLUME ["/config", "/logs", "/media"]

RUN apk update && \
    apk add --no-cache \
    build-base \
    linux-headers

COPY requirements.txt requirements.txt
# 修改pip安装命令部分，添加清华镜像源
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt && \
    rm requirements.txt

COPY --from=builder /builder/app /app

RUN apk del build-base linux-headers && \
    rm -rf /tmp/*

ENTRYPOINT ["python", "/app/main.py"]