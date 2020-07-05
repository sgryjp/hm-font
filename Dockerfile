FROM sgryjp/fontforge:focal

RUN mkdir inputs outputs
RUN curl -fsSL https://github.com/source-foundry/Hack/releases/download/v3.003/Hack-v3.003-ttf.tar.xz | \
    xz -d - | tar xv -C inputs
RUN curl -fsSL https://osdn.net/projects/mplus-fonts/downloads/62344/mplus-TESTFLIGHT-063a.tar.xz | \
    xz -d - | tar xv -C inputs && \
    mv inputs/mplus-TESTFLIGHT-063a/mplus-1m-regular.ttf inputs
RUN find inputs -type f
COPY LICENSE .
COPY build.py .

CMD python3 build.py -i inputs -o outputs
