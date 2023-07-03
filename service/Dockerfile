
# FROM nvidia/cuda:11.2.2-cudnn8-runtime
# #Меньше весит

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# RUN apt-key del 7fa2af80
# RUN rm /etc/apt/sources.list.d/cuda.list
# RUN rm /etc/apt/sources.list.d/nvidia-ml.list
# RUN apt-get update
# RUN apt-get install wget unzip zip -y
# RUN apt-get install -y --no-install-recommends wget
# RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
# RUN dpkg -i cuda-keyring_1.0-1_all.deb
# # Install pip from standard ubuntu packages
# RUN apt-get install software-properties-common -y
# RUN add-apt-repository ppa:deadsnakes/ppa
# RUN apt-get update
# # Install py39 from deadsnakes repository
# RUN apt-get install python3.9 -y
# RUN which python3.9
# RUN ln -sf /usr/bin/python3.9 /usr/bin/python3
# # Install pip from standard ubuntu packages
# RUN apt-get install python3-pip -y
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     gcc \
#     software-properties-common \
#     ffmpeg \
#     libsndfile1-dev \
#     && rm -rf /var/lib/apt/lists/*

# RUN mkdir /service
# COPY /service /service
# WORKDIR /service
# RUN pip install -r requirements.txt

FROM python:3.9 as ptn

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY . .
WORKDIR .
RUN pip install -r requirements.txt


FROM nvidia/cuda:11.2.2-cudnn8-runtime
WORKDIR .
COPY --from=ptn . .
