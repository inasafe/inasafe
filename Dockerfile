#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM ubuntu:trusty
MAINTAINER Tim Sutton<tim@kartoza.com>

#RUN  export DEBIAN_FRONTEND=noninteractive
#ENV  DEBIAN_FRONTEND noninteractive
#RUN  dpkg-divert --local --rename --add /sbin/initctl


# Use local cached debs from host (saves your bandwidth!)
# Change ip below to that of your apt-cacher-ng host
# Or comment this line out if you do not with to use caching
#ADD 71-apt-cacher-ng /etc/apt/apt.conf.d/71-apt-cacher-ng


#RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty main restricted universe" > /etc/apt/sources.list
#RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-updates main restricted" >> /etc/apt/sources.list
#RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty universe" >> /etc/apt/sources.list
#RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-updates universe" >> /etc/apt/sources.list
#RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-security main restricted" >> /etc/apt/sources.list
#RUN echo "deb http://archive.ubuntu.com/ubuntu/ trusty-security universe" >> /etc/apt/sources.list
#RUN echo "deb http://archive.ubuntu.com/ubuntu trusty main universe" >> /etc/apt/sources.list

RUN echo "deb http://qgis.org/debian trusty main" >> /etc/apt/sources.list
RUN echo "deb http://ppa.launchpad.net/ubuntugis/ubuntugis-unstable/ubuntu trusty main" >> /etc/apt/sources.list
RUN apt-get update -y

#-------------Application Specific Stuff ----------------------------------------------------
RUN apt-get install -y \
    build-essential \
    xvfb \
    git \
    python-pip \
    xvfb \
    python-nose \
    python-coverage \
    pyflakes \
    python-nosexcover \
    python-scientific

RUN pip install pep8 pylint

RUN gpg --keyserver keyserver.ubuntu.com --recv DD45F6C3
RUN gpg --export --armor DD45F6C3 | sudo apt-key add -

RUN apt-get install -y --force-yes \
    qgis \
    python-qgis

ENV QGIS_PREFIX_PATH /usr
ENV PYTHONPATH ${QGIS_PREFIX_PATH}/share/qgis/python/:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:`pwd`:/insafe:/
ENV LD_LIBRARY_PATH ${QGIS_PREFIX_PATH}/share/qgis/python/plugins/
ENV LD_LIBRARY_PATH ${QGIS_PREFIX_PATH}/lib

# Mount inasafe and insafe_data under /
RUN mkdir /inasafe
WORKDIR /inasafe

#ENTRYPOINT ["make"]


# Here we list packages to test by default
#CMD ["safe_qgis"]
CMD ["make docker-test"]
