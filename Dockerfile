FROM alpine:latest
RUN apk --update add python3
COPY interpreter.py /interpreter.py
COPY script.sh /script
RUN chmod 755 /script

# sudo docker run -iv `pwd`:/code:ro hyp_tes /script /code/cat.hyp

