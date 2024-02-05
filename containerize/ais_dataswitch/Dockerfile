FROM conda/miniconda3
RUN conda create -n env python=3.8
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

WORKDIR /ais_data_switch

COPY . .

EXPOSE 3336

CMD ["python", "./ais_dataswitch.py"]