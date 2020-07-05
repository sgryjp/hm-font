FROM sgryjp/fontforge:focal

RUN curl -fsSLO https://github.com/source-foundry/Hack/releases/download/v3.003/Hack-v3.003-ttf.tar.xz && \
    tar xf Hack-v3.003-ttf.tar.xz
RUN curl -fsSLO https://osdn.net/projects/mplus-fonts/downloads/62344/mplus-TESTFLIGHT-063a.tar.xz && \
    tar xf mplus-TESTFLIGHT-063a.tar.xz && \
    mv mplus-TESTFLIGHT-063a/mplus-1m-regular.ttf .
COPY LICENSE LICENSE
COPY build.py build.py

CMD python3 build.py -o output/hm-regular.ttf
