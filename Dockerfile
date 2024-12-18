# Use an official Python runtime as a parent image
FROM python:3.11.7

# 设置工作目录
WORKDIR /app

# 将项目依赖文件复制到容器中
COPY requirements.txt ./

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将项目文件复制到容器中
COPY . .

# 环境变量配置
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]