FROM centos:7

RUN yum install -y epel-release curl git make patch
RUN yum install -y golang rpm-build-libs rpmdevtools
RUN rpmdev-setuptree
ENV GOVERSION=1.9.1
RUN curl -sSL https://storage.googleapis.com/golang/go${GOVERSION}.linux-amd64.tar.gz | tar zxf - -C /usr/local && ln -sfn ../go/bin/go /usr/local/bin/
RUN GOPATH=/usr/share/gocode go get github.com/aws/aws-sdk-go/...
ADD . /root/rpmbuild/SOURCES/
ADD caddy.spec /root/rpmbuild/SPECS/
RUN spectool -R -g /root/rpmbuild/SPECS/caddy.spec
ENV VERSION=0.10.10 ITERATION=5
RUN rpmbuild -bb /root/rpmbuild/SPECS/caddy.spec
CMD cp /root/rpmbuild/RPMS/x86_64/caddy-${VERSION}-${ITERATION}.el7.centos.x86_64.rpm /output && chown $(stat -c %u /output):$(stat -c %g /output) /output/caddy-${VERSION}-${ITERATION}.el7.centos.x86_64.rpm
