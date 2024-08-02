# 使用官方Python运行时作为父镜像
FROM python:3.12.4

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到位于/app的容器中
COPY . /app

# 设置清华源
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装指定的Python库
RUN pip install langchain 
RUN pip install langchain_core 
RUN pip install langchain_openai 
RUN pip install langchain_anthropic 
RUN pip install langchain_community 
RUN pip install flask 
RUN pip install flask_cors 
RUN pip install python-dotenv 
RUN pip install pydantic 
RUN pip install requests 
RUN pip install beautifulsoup4
RUN pip install unstructured
RUN pip install crewai 

# 开放6000端口
EXPOSE 6000

# 运行server.py
CMD ["python", "server.py"]
