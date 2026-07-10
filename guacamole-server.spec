Name:		guacamole-server
Version:	1.6.0
Release:	1%{?dist}
Summary:	Guacamole Server

License:	Apache-2.0
URL:		https://guacamole.apache.org/
ExclusiveArch:	x86_64 aarch64
Source0:	https://downloads.apache.org/guacamole/%{version}/source/%{name}-%{version}.tar.gz
Source1:	https://downloads.apache.org/guacamole/%{version}/binary/guacamole-%{version}.war
Source2:	https://downloads.apache.org/guacamole/%{version}/binary/guacamole-auth-ldap-%{version}.tar.gz

%if 0%{?suse_version}
%global freerdp_devel_pkg freerdp2-devel
%global libjpeg_devel_pkg libjpeg8-devel
%global libvncserver_devel_pkg LibVNCServer-devel
%global openssl_devel_pkg libopenssl-devel
%else
%global freerdp_devel_pkg freerdp-devel
%global libjpeg_devel_pkg libjpeg-turbo-devel
%global libvncserver_devel_pkg libvncserver-devel
%global openssl_devel_pkg openssl-devel
%endif

BuildRequires:  cairo-devel
BuildRequires:	%{freerdp_devel_pkg}
BuildRequires:  %{libjpeg_devel_pkg}
BuildRequires:	libogg-devel
BuildRequires:	libpng-devel
BuildRequires:	libssh2-devel
BuildRequires:	%{libvncserver_devel_pkg}
BuildRequires:	libvorbis-devel
BuildRequires:	libwebp-devel
BuildRequires:	%{openssl_devel_pkg}
BuildRequires:	pango-devel
BuildRequires:	pulseaudio-libs-devel
BuildRequires:	uuid-devel
BuildRequires:	systemd-rpm-macros
%{?systemd_requires}

%description
Guacamole is a clientless remote desktop gateway. It supports standard
protocols like VNC, RDP, and SSH.

%package -n guacamole-client
Summary:	The guacamole client
Requires:	tomcat
Requires:	%{name} = %{version}

%description -n guacamole-client
The Guacamole web application providing the client-side interface.

%package -n guacamole-auth-ldap
Summary:	Guacamole LDAP authentication module
Requires:	%{name} = %{version}

%description -n guacamole-auth-ldap
LDAP authentication extension for Apache Guacamole.

%prep
%setup -q -T -D -b 2 -n guacamole-auth-ldap-%{version}
%setup -qn %{name}-%{version}

%build
%configure --with-init-dir=%{_initddir}
%make_build

%install
%make_install
# Client
%{__install} -d %{buildroot}%{_sysconfdir}/guacamole
%{__install} -d %{buildroot}%{_datadir}/tomcat
%{__install} -d %{buildroot}%{_var}/lib/tomcat/webapps
%{__ln_s} %{_sysconfdir}/guacamole %{buildroot}%{_datadir}/tomcat/.guacamole
%{__install} -m 444 %{SOURCE1} %{buildroot}%{_var}/lib/tomcat/webapps/guacamole.war

cat <<EOF > %{buildroot}%{_sysconfdir}/guacamole/guacamole.properties
# Minimal Guacamole Properties file
api-session-timeout:		14400
guacd-hostname:			localhost
guacd-port:			4822
EOF

cat <<EOF > %{buildroot}%{_sysconfdir}/guacamole/user-mapping.xml
<user-mapping>
<!-- Per-user authentication and config information -->
    <authorize username="test" password="password">
        <protocol>ssh</protocol>
        <param name="hostname">localhost</param>
        <param name="port">22</param>
        <param name="username">UserName</param>
        <param name="password">UserPassword</param>
    </authorize>
</user-mapping>
EOF

# Auth LDAP
%{__install} -d %{buildroot}%{_datadir}/guacamole/auth-ldap
%{__install} -d %{buildroot}%{_sysconfdir}/guacamole/extensions
cd ../guacamole-auth-ldap-%{version}

%{__install} -m 444 guacamole-auth-ldap-%{version}.jar %{buildroot}%{_sysconfdir}/guacamole/extensions
%{__rm} guacamole-auth-ldap-%{version}.jar
%{__cp} -r * %{buildroot}%{_datadir}/guacamole/auth-ldap/

%post
%systemd_post guacd.service

%preun
%systemd_preun guacd.service

%postun
%systemd_postun_with_restart guacd.service

%post -n guacamole-client
%systemd_post tomcat.service

%preun -n guacamole-client
%systemd_preun tomcat.service

%postun -n guacamole-client
%systemd_postun_with_restart tomcat.service

%files
%license LICENSE
%{_initddir}/*
%{_includedir}/guacamole/*
%{_libdir}/freerdp/*
%{_libdir}/libguac*
%{_sbindir}/guacd
%{_bindir}/guacenc
%doc
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n guacamole-client
%{_var}/lib/tomcat/webapps/*
%config(noreplace) %{_sysconfdir}/guacamole/guacamole.properties
%config(noreplace) %{_sysconfdir}/guacamole/user-mapping.xml
%config(noreplace) %{_datadir}/tomcat/.guacamole

%files -n guacamole-auth-ldap
%{_sysconfdir}/guacamole/extensions/*
%doc
%{_datadir}/guacamole/auth-ldap/

%changelog
* Sat Jul 05 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.6.0-1
- Add openSUSE/SLES package name guards (verified against openSUSE Tumbleweed
  repos): freerdp-devel -> freerdp2-devel, libjpeg-turbo-devel -> libjpeg8-devel,
  libvncserver-devel -> LibVNCServer-devel (case differs, RPM names are
  case-sensitive), openssl-devel -> libopenssl-devel (org-documented divergence)
- Remove stray commented #BuildArch: noarch lines from guacamole-client and
  guacamole-auth-ldap subpackages; ExclusiveArch is already inherited from
  the top-level package, no per-subpackage declaration needed
- cairo-devel, libogg-devel, libpng-devel, libssh2-devel, libvorbis-devel,
  libwebp-devel, pango-devel, pulseaudio-libs-devel, uuid-devel,
  systemd-rpm-macros verified identical on openSUSE Tumbleweed, left unguarded

* Sat Jul 04 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.6.0-1
- Source0/1/2: Apache downloads URLs verified (1.6.0 is current, all HTTP 200)
- Add ExclusiveArch: x86_64 aarch64; systemd-rpm-macros; %%{?systemd_requires}; %%license LICENSE

* Fri May 22 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.6.0-1
- Fix spec violations: replace deprecated %__macro forms, use %{buildroot} macros, use systemd scriptlet macros

* Fri Apr 24 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 1.6.0-1
- Update to 1.6.0
- Modernize spec for AlmaLinux 10
