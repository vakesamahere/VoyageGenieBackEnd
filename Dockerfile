# 使用官方Python运行时作为父镜像
FROM python:3.12.4

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到位于/app的容器中
COPY . /app

# 设置清华源
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装指定的Python库
RUN pip install langchain \
langchain_core \
langchain_openai \
langchain_anthropic \
langchain_community \
flask \
flask_cors \
python-dotenv \
pydantic \
requests \
beautifulsoup4 \
unstructured \
crewai 

# 开放6000端口
EXPOSE 6000

# 运行server.py
CMD ["python", "server.py"]
