FROM nvidia/cudagl:10.2-base-ubuntu18.04

WORKDIR /mirror/

RUN apt-get update && \
  apt-get -y install python3-pip python3-pyaudio python3.7 libusb-1.0-0-dev \
  libgl1-mesa-glx nano git curl libasound2 chromium-browser \
  libgtk-3-0 reptyr

RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase
RUN ln -s /usr/bin/chromium-browser /usr/bin/chromium
ENV DEVICE cpu
RUN useradd -m -s /bin/bash miroir

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN pip3 install --upgrade pip

ADD build/cpu/requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod -R 777 /mirror/
RUN chmod -R 777 /usr/local/lib/python3.7/dist-packages/mediapipe/modules/

CMD su miroir -s /bin/bash -c "python3 init.py"
