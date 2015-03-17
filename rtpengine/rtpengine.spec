Name:      rtpengine
Version:   3.7.2.1
Release:   1%{?dist}
Summary:   The Sipwise NGCP rtpengine
Group:     System Environment/Daemons
License:   GPLv3
URL:       https://github.com/sipwise/rtpengine
Source0:   https://github.com/sipwise/rtpengine/archive/%{version}/%{name}-%{version}.tar.gz
Source1:   rtpengine.service
Source2:   rtpengine.sysconfig
Source3:   rtpengine-dkms.conf.in
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: pkgconfig glib2-devel zlib-devel openssl-devel pcre-devel libcurl-devel xmlrpc-c-devel
Requires: glibc zlib openssl pcre libcurl xmlrpc-c

%description
The Sipwise NGCP rtpengine is a proxy for RTP traffic and other UDP based
media traffic. It's meant to be used with the OpenSips SIP proxy and forms a
drop-in replacement for any of the other available RTP and media proxies.

%package dkms
Summary:         Kernel module for NGCP rtpengine in-kernel packet forwarding
Group:           System Environment/Daemons
BuildArch:       noarch
Requires:        gcc make redhat-rpm-config kernel-devel kernel-headers
Requires(post):  epel-release dkms
Requires(preun): epel-release dkms

%description dkms
Kernel module for rtpengine in-kernel packet forwarding

%package kernel
Summary:       NGCP rtpengine in-kernel packet forwarding
Group:         System Environment/Daemons
BuildRequires: iptables-devel kernel-devel kernel-headers
Obsoletes:     %{name}-kernel < %{version}
Requires:      iptables iptables-ipv6 rtpengine = %{version}
Requires:      rtpengine-dkms = %{version}

%description kernel
NGCP rtpengine in-kernel packet forwarding

%prep
%setup -q

%build
RTPENGINE_VERSION="\"%{version}-%{release}\""
pushd daemon
make
popd
pushd iptables-extension
make
popd

%install
# Install the userspace daemon
install -D -p -m755 daemon/rtpengine %{buildroot}%{_sbindir}/rtpengine

## Install the systemd script and configuration file
install -D -p -m644 %{SOURCE1} \
	%{buildroot}%{_sysconfdir}/systemd/system/rtpengine
install -D -p -m644 %{SOURCE2} \
	%{buildroot}%{_sysconfdir}/sysconfig/rtpengine
mkdir -p %{buildroot}%{_sharedstatedir}/rtpengine

# Install the iptables plugin
install -D -p -m755 iptables-extension/libxt_RTPENGINE.so \
	%{buildroot}/%{_lib}/xtables/libxt_RTPENGINE.so

## DKMS module source install
install -D -p -m644 kernel-module/Makefile \
	 %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/Makefile
install -D -p -m644 kernel-module/xt_RTPENGINE.c \
	 %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/xt_RTPENGINE.c
install -D -p -m644 kernel-module/xt_RTPENGINE.h \
	 %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/xt_RTPENGINE.h
sed "s/__VERSION__/%{version}-%{release}/g" %{SOURCE3} > \
	%{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/dkms.conf

%clean
rm -rf %{buildroot}

%pre
/usr/sbin/groupadd -r rtpengine 2> /dev/null || :
/usr/sbin/useradd -r -g rtpengine -s /sbin/nologin -c "RTP Engine Daemon" \
	-d %{_sharedstatedir}/rtpengine rtpengine \
	2> /dev/null || :

%post
if [ $1 -eq 1 ]; then
   /bin/systemctl enable %{name} || :
fi

%post dkms
# Add to DKMS registry, build, and install module
dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --force
true

%preun
if [ $1 = 0 ] ; then
	/bin/systemctl stop %{name}
	/bin/systemctl disable %{name}
fi

%preun dkms
# Remove from DKMS registry
dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all
true

%files
# Userspace daemon
%{_sbindir}/rtpengine

# systemd script and configuration file
%{_sysconfdir}/systemd/system/rtpengine
%config(noreplace) %{_sysconfdir}/sysconfig/rtpengine
%dir %{_sharedstatedir}/rtpengine

# Documentation
%doc LICENSE README.md el/README.el.md debian/changelog debian/copyright

%files kernel
/%{_lib}/xtables/libxt_RTPENGINE.so

%files dkms
%attr(0755,root,root) %{_usrsrc}/%{name}-%{version}-%{release}/

%changelog
* Tue Mar 17 2015 Rob Gagnon - 3.7.2.1
- Updated for version mr3.7.2.1
- Ported to CentOS 7

* Mon Nov 11 2013 Peter Dunkley <peter.dunkley@crocodilertc.net>
  - Updated version to 2.3.2
  - Set license to GPLv3
* Thu Aug 15 2013 Peter Dunkley <peter.dunkley@crocodilertc.net>
  - init.d scripts and configuration file
* Wed Aug 14 2013 Peter Dunkley <peter.dunkley@crocodilertc.net>
  - First version of .spec file
  - Builds and installs userspace daemon (but no init.d scripts etc yet)
  - Builds and installs the iptables plugin
  - DKMS package for the kernel module
