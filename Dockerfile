FROM node AS stage

WORKDIR /app
COPY ./UI .
WORKDIR /app/xmigrate-ui
RUN yarn && yarn build

FROM ubuntu:18.04

WORKDIR /app

RUN apt update -y 
RUN apt install -y python3.7
RUN apt install -y python3-pip
RUN apt install -y wget nginx

RUN wget http://launchpadlibrarian.net/422997913/qemu-utils_2.0.0+dfsg-2ubuntu1.46_amd64.deb && apt install ./qemu-utils_2.0.0+dfsg-2ubuntu1.46_amd64.deb -y

RUN wget https://azcopyvnext.azureedge.net/release20201021/azcopy_linux_amd64_10.6.1.tar.gz && \
    tar -zxf ./azcopy_linux_amd64_10.6.1.tar.gz && \
    mv ./azcopy_linux_amd64_10.6.1/azcopy /usr/bin  

COPY nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p ./logs/ansible/ && mkdir osdisks && touch ./logs/ansible/log.txt && touch ./logs/ansible/migration_log.txt && touch ./logs/ansible/azcopy_log.txt

COPY requirements.txt requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN python3.7 -m pip install -U pip

RUN python3.7 -m pip install setuptools-rust

RUN python3.7 -m pip install --no-use-pep517 --upgrade pyOpenSSL

RUN python3.7 -m pip install -r requirements.txt 

COPY --from=stage /app/xmigrate-ui/build /usr/share/nginx/html/

COPY . .
RUN rm -rf UI
ENV AZCOPY_BUFFER_GB=0.3
EXPOSE 80
ENTRYPOINT ["/bin/sh", "./scripts/start.sh"]

