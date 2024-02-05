FROM conda/miniconda3
RUN conda create -n env python=3.8
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

WORKDIR /ais_udp_server

COPY . .

EXPOSE 10000

CMD ["python", "./ais_udpServer.py"]