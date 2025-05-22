FROM python:3.10.16
LABEL authors="Kater_kcl"

COPY src /maj/src
COPY config /maj/config
COPY static /maj/static
COPY Temp /maj/Temp
COPY app.py /maj/
COPY requirements.txt /maj/

WORKDIR /maj
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /orph/requirements.txt

EXPOSE 1234

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:1234", "main:app"]
