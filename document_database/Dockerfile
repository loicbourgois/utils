FROM python
RUN apt-get update \
    && apt-get install -y autossh screen postgresql-client 
    # && \
    # wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy && \
    # chmod +x cloud_sql_proxy && \
    # mkdir -p /root/github.com/bin/ && \
    # mv cloud_sql_proxy /root/github.com/bin/cloud_sql_proxy
COPY ./document_database/requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip python -m pip install -r requirements.txt
CMD ["/root/utils/document_database/inner.sh"]
