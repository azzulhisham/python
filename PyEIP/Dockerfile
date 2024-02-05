FROM conda/miniconda3
RUN conda create -n env python=3.6
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

RUN conda install -c anaconda pymssql

WORKDIR /pyeip

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./app ./app

EXPOSE 3838

CMD ["python", "./app/main.py"]