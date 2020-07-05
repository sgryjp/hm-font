FROM sgryjp/fontforge:focal

ENV FOO=/foo
ENV INPUT_FOO=/input_foo
RUN echo "${FOO}" "${INPUT_FOO}" "${GITHUB_WORKSPACE}"

RUN mkdir /app /app/output
WORKDIR /app

RUN curl -fsSLO https://github.com/source-foundry/Hack/releases/download/v3.003/Hack-v3.003-ttf.tar.xz && \
    tar xvf Hack-v3.003-ttf.tar.xz
RUN curl -fsSLO https://osdn.net/projects/mplus-fonts/downloads/62344/mplus-TESTFLIGHT-063a.tar.xz && \
    tar xvf mplus-TESTFLIGHT-063a.tar.xz && \
    mv mplus-TESTFLIGHT-063a/mplus-1m-regular.ttf .
COPY LICENSE .
COPY build.py .

CMD python3 /app/build.py -i /app -o /app/output
