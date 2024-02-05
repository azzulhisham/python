FROM conda/miniconda3
RUN conda create -n env python=3.8
RUN echo "source activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH


WORKDIR /pyvts

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install crate
RUN pip install Flask-Cors


COPY ./app ./app

EXPOSE 3838

CMD ["python", "./app/main.py"]