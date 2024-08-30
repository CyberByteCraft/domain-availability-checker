FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postfix \
    mailutils \
    busybox-syslogd \
    ca-certificates \
    && pip install --no-cache-dir python-whois discord.py

COPY configs/main.cf /etc/postfix/main.cf

RUN sed -i "s/\$mydomain/${POSTFIX_MYDOMAIN:-example.com}/g" /etc/postfix/main.cf && \
    echo "${EMAIL_FROM:-domainchecker@example.com}" > /etc/mailname

RUN mkdir -p /var/log && touch /var/log/mail.log

COPY domain_check.py /app

CMD ["sh", "-c", "syslogd -O /var/log/mail.log && service postfix start && exec python domain_check.py"]
