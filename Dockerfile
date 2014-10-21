#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM ubuntu:trusty
MAINTAINER Tim Sutton<tim@linfiniti.com>

RUN  export DEBIAN_FRONTEND=noninteractive
ENV  DEBIAN_FRONTEND noninteractive
RUN  dpkg-divert --local --rename --add /sbin/initctl


# Use local cached debs from host (saves your bandwidth!)
# Change ip below to that of your apt-cacher-ng host
# Or comment this line out if you do not with to use caching
ADD 71-apt-cacher-ng /etc/apt/apt.conf.d/71-apt-cacher-ng


RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty main restricted universe" > /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-updates main restricted" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty universe" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-updates universe" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-security main restricted" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-security universe" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu trusty main universe" >> /etc/apt/sources.list
RUN apt-get update -y

#-------------Application Specific Stuff ----------------------------------------------------

RUN sudo apt-get install -y \
    build-essential \
    xvfb \
    git \
    qgis \
    python-qgis \
    pylint \
    pep8 \
    xvfb \
    python-nose \
    python-coverage \
    pyflakes \
    python-nosexcover \
    python-scientific \
    python-beautifulsoup

ENV QGIS_PREFIX_PATH /usr
ENV PYTHONPATH ${QGIS_PREFIX_PATH}/share/qgis/python/:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:`pwd`:/insafe-tests
ENV LD_LIBRARY_PATH ${QGIS_PREFIX_PATH}/share/qgis/python/plugins/
ENV LD_LIBRARY_PATH ${QGIS_PREFIX_PATH}/lib

# Mount insafe-dev and insafe_data under insafe-tests
RUN mkdir /inasafe-tests
WORKDIR /inasafe-tests

#ENTRYPOINT ["make"]


# Here we list packages to test by default
#CMD ["safe_qgis"]
CMD ["make docker-test"]
