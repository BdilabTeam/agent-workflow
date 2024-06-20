FROM python:3.10-slim

# 设置 DEBIAN_FRONTEND 环境变量以避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 确保 /tmp 目录具有适当权限
RUN chmod 1777 /tmp

# 切换到 root 用户并安装必要的软件包
USER root

RUN apt-get update && \
    apt-get install -y gcc g++ git make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建一个新的用户
RUN useradd -m -u 1000 user

# 切换到新创建的用户
USER user

# 设置环境变量
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 设置工作目录
WORKDIR $HOME/app

# 复制并设置权限
COPY --chown=user . $HOME/app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt requirements.txt
RUN pip install --user -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 启动命令
# CMD ["langflow", "run", "--host", "0.0.0.0"]

