# base image
FROM python:3.10.0

WORKDIR /app


# copy over and install packages
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# exposing default port for streamlit
EXPOSE 8501

# copying everything over
COPY . /app

ENTRYPOINT ["streamlit", "run"]

# run app
CMD ["app.py"]
#CMD [ "streamlit run app.py" ]

