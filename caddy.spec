# plugins
%bcond_without dnsproviders
%bcond_without realip

%bcond_with debug

%if %{with debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%if ! 0%{?gobuild:1}
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};
%endif

# caddy
%global import_path github.com/mholt/caddy

# dnsproviders
%global import_path_dnsproviders github.com/caddyserver/dnsproviders
%global commit_dnsproviders 8c9fc0487be7ce4d5cfa6f509c58150033eaa23e

# lego
%global import_path_lego github.com/xenolf/lego
%global commit_lego 49b9503635ff26b2b725667de187f05d5960acd0

# realip
%global import_path_realip github.com/captncraig/caddy-realip
%global commit_realip 5dd1f4047d0f649f21ba9f8d7e491d712be9a5b0

Name: caddy
Version: 0.10.9
Release: 4%{?dist}
Summary: HTTP/2 web server with automatic HTTPS
License: ASL 2.0 and MIT
URL: https://caddyserver.com
Source0: https://%{import_path}/archive/v%{version}/caddy-%{version}.tar.gz
Source1: https://%{import_path_dnsproviders}/archive/%{commit_dnsproviders}/dnsproviders-%{commit_dnsproviders}.tar.gz
Source2: https://%{import_path_lego}/archive/%{commit_lego}/lego-%{commit_lego}.tar.gz
Source3: https://%{import_path_realip}/archive/%{commit_realip}/realip-%{commit_realip}.tar.gz
Source10: caddy.conf
Source11: caddy.service
Source12: index.html
Patch0: 0001-Remove-Caddy-Sponsors-header.patch
ExclusiveArch: %{go_arches}
# fails to build on s390x
ExcludeArch: s390x
%{?go_compiler:BuildRequires: compiler(go-compiler)}
BuildRequires: golang >= 1.8
BuildRequires: systemd
%{?systemd_requires}
Provides: webserver


%description
Caddy is the HTTP/2 web server with automatic HTTPS.


%prep
%autosetup -p1


%if %{with dnsproviders}
mkdir -p vendor/%{import_path_dnsproviders}
tar -C vendor/%{import_path_dnsproviders} --strip-components 1 -x -f %{S:1}
mkdir -p vendor/%{import_path_lego}
tar -C vendor/%{import_path_lego} --strip-components 1 -x -f %{S:2}
%endif

%if %{with realip}
mkdir -p vendor/%{import_path_realip}
tar -C vendor/%{import_path_realip} --strip-components 1 -x -f %{S:3}
%endif

sed \
%if %{with dnsproviders}
    -e '/other plugins/ a \\t_ "%{import_path_dnsproviders}/route53"' \
    -e '/other plugins/ a \\t_ "%{import_path_dnsproviders}/cloudflare"' \
    -e '/other plugins/ a \\t_ "%{import_path_dnsproviders}/digitalocean"' \
    -e '/other plugins/ a \\t_ "%{import_path_dnsproviders}/dyn"' \
    -e '/other plugins/ a \\t_ "%{import_path_dnsproviders}/gandi"' \
    -e '/other plugins/ a \\t_ "%{import_path_dnsproviders}/namecheap"' \
    -e '/other plugins/ a \\t_ "%{import_path_dnsproviders}/rackspace"' \
%endif
%if %{with realip}
    -e '/other plugins/ a \\t_ "%{import_path_realip}"' \
%endif
    -i caddy/caddymain/run.go

mv vendor/%{import_path_dnsproviders}/LICENSE LICENSE-dnsproviders
mv vendor/%{import_path_lego}/LICENSE LICENSE-lego
mv vendor/%{import_path_realip}/LICENSE LICENSE-realip


%build
mkdir -p src/%(dirname %{import_path})
ln -s ../../.. src/%{import_path}
export GOPATH=$(pwd):%{gopath}
export LDFLAGS="-X %{import_path}/caddy/caddymain.gitTag=v%{version}"
%gobuild -o bin/caddy %{import_path}/caddy


%install
install -D -m 0755 bin/caddy %{buildroot}%{_bindir}/caddy
install -D -m 0644 %{S:10} %{buildroot}%{_sysconfdir}/caddy/caddy.conf
install -D -m 0644 %{S:11} %{buildroot}%{_unitdir}/caddy.service
install -D -m 0644 %{S:12} %{buildroot}%{_datadir}/caddy/index.html
install -d -m 0755 %{buildroot}%{_sysconfdir}/caddy/conf.d
install -d -m 0750 %{buildroot}%{_sharedstatedir}/caddy


%pre
getent group caddy &> /dev/null || \
groupadd -r caddy &> /dev/null
getent passwd caddy &> /dev/null || \
useradd -r -g caddy -d %{_sharedstatedir}/caddy -s /sbin/nologin -c 'Caddy web server' caddy &> /dev/null
exit 0


%post
setcap cap_net_bind_service=+ep %{_bindir}/caddy
%systemd_post caddy.service


%preun
%systemd_preun caddy.service


%postun
%systemd_postun_with_restart caddy.service


%files
%license dist/LICENSES.txt LICENSE-dnsproviders LICENSE-lego LICENSE-realip
%doc dist/README.txt
%{_bindir}/caddy
%{_datadir}/caddy
%{_unitdir}/caddy.service
%dir %{_sysconfdir}/caddy
%dir %{_sysconfdir}/caddy/conf.d
%config(noreplace) %{_sysconfdir}/caddy/caddy.conf
%attr(0750,caddy,caddy) %dir %{_sharedstatedir}/caddy


%changelog
* Mon Sep 18 2017 Carl George <carl@george.computer> - 0.10.9-4
- Exclude s390x

* Sun Sep 17 2017 Carl George <carl@george.computer> - 0.10.9-3
- Add realip plugin
- Add conditionals for plugins

* Sat Sep 16 2017 Carl George <carl@george.computer> - 0.10.9-2
- Add sources for caddyserver/dnsproviders and xenolf/lego
- Disable all dns providers that require additional libraries (dnsimple, dnspod, googlecloud, linode, ovh, route53, vultr)
- Rewrite default index.html

* Tue Sep 12 2017 Carl George <carl@george.computer> - 0.10.9-1
- Latest upstream
- Add config validation to unit file
- Disable exoscale dns provider https://github.com/xenolf/lego/issues/429

* Fri Sep 08 2017 Carl George <carl@george.computer> - 0.10.8-1
- Latest upstream
- Build with %%gobuild macro
- Move config subdirectory from /etc/caddy/caddy.conf.d to /etc/caddy/conf.d

* Tue Aug 29 2017 Carl George <carl@george.computer> - 0.10.7-1
- Latest upstream

* Fri Aug 25 2017 Carl George <carl@george.computer> - 0.10.6-2
- Use SIQQUIT to stop service
- Increase the process limit from 64 to 512
- Only `go get` in caddy/caddymain

* Fri Aug 11 2017 Carl George <carl@george.computer> - 0.10.6-1
- Latest upstream
- Add webserver virtual provides
- Drop tmpfiles and just own /var/lib/caddy directly
- Remove PrivateDevices setting from unit file, it prevents selinux process transitions
- Disable rfc2136 dns provider https://github.com/caddyserver/dnsproviders/issues/11

* Sat Jun 03 2017 Carl George <carl.george@rackspace.com> - 0.10.3-2
- Rename Envfile to envfile
- Rename Caddyfile to caddy.conf
- Include additional configs from caddy.conf.d directory

* Fri May 19 2017 Carl George <carl.george@rackspace.com> - 0.10.3-1
- Latest upstream

* Mon May 15 2017 Carl George <carl.george@rackspace.com> - 0.10.2-1
- Initial package
