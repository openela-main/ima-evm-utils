%global compat_soversion 0

Name:    ima-evm-utils
Version: 1.3.2
Release: 12%{?dist}
Summary: IMA/EVM support utilities
License: GPLv2
Url:     http://linux-ima.sourceforge.net/
Source:  http://sourceforge.net/projects/linux-ima/files/ima-evm-utils/%{name}-%{version}.tar.gz
Source10: ima-evm-utils-1.1.tar.gz

Patch0: 0001-Fix-sign_hash-not-observing-the-hashalgo-argument.patch
# compat patches
Patch1: docbook-xsl-path.patch
Patch2: covscan-memory-leaks.patch
Patch3: annocheck-opt-flag.patch
Patch4: libimaevm-keydesc-import.patch

BuildRequires: asciidoc
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gcc
BuildRequires: keyutils-libs-devel
BuildRequires: libtool
BuildRequires: libxslt
BuildRequires: openssl-devel
BuildRequires: tpm2-tss-devel
# compat requirement
BuildRequires: libattr-devel

#Requires: tpm2-tss

%description
The Trusted Computing Group(TCG) run-time Integrity Measurement Architecture
(IMA) maintains a list of hash values of executables and other sensitive
system files, as they are read or executed. These are stored in the file
systems extended attributes. The Extended Verification Module (EVM) prevents
unauthorized changes to these extended attributes on the file system.
ima-evm-utils is used to prepare the file system for these extended attributes.

%package devel
Summary: Development files for %{name}
Requires: %{name} = %{version}-%{release}

%description devel
This package provides the header files for %{name}

%package -n %{name}%{compat_soversion}
Summary: Compatibility package of %{name}

%description -n %{name}%{compat_soversion}
This package provides the libimaevm.so.%{compat_soversion} relative to %{name}-1.1

%prep
%setup -q
%patch0 -p1
mkdir compat/
tar -zxf %{SOURCE10} --strip-components=1 -C compat/
cd compat/
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
# build compat version of the package
pushd compat/
autoreconf -vif
%configure --disable-static
%make_build
popd

autoreconf -vif
%configure --disable-static
%make_build

%install
%make_install
find %{buildroot}%{_libdir} -type f -name "*.la" -print -delete
# install compat libs
pushd compat/src/.libs/
install -p libimaevm.so.%{compat_soversion}.0.0 %{buildroot}%{_libdir}/libimaevm.so.%{compat_soversion}.0.0
ln -s -f %{buildroot}%{_libdir}/libimaevm.so.%{compat_soversion}.0.0 %{buildroot}%{_libdir}/libimaevm.so.%{compat_soversion}
popd

%ldconfig_scriptlets

%files
%license COPYING
%doc NEWS README AUTHORS
%{_bindir}/*
# if you need to bump the soname version, coordinate with dependent packages
%{_libdir}/libimaevm.so.2
%{_libdir}/libimaevm.so.2.0.0
%{_mandir}/man1/*

%files devel
%{_pkgdocdir}/*.sh
%{_includedir}/*
%{_libdir}/libimaevm.so

%files -n %{name}%{compat_soversion}
%{_libdir}/libimaevm.so.%{compat_soversion}
%{_libdir}/libimaevm.so.%{compat_soversion}.0.0

%changelog
* Thu Feb 18 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-12
- Add compat subpackage for keeping the API stability in userspace

* Mon Jan 25 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-11
- Bump release number for yet another rebuild

* Mon Jan 25 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-10
- Add patch for fixing hash algorithm used through libimaevm

* Fri Jan 15 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-9
- Add tpm2-tss as a runtime dependency

* Sun Jan 10 2021 Michal Domonkos <mdomonko@redhat.com> - 1.3.2-8
- Bump release number for yet another couple of rebuilds

* Wed Jan 06 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-4
- Bump release number for yet another build for solving wrong target usage

* Wed Jan 06 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-3
- Bump release number for another build, handling build issues

* Tue Dec 01 2020 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-2
- Bump release number for forcing a new build

* Mon Nov 09 2020 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-1
- Rebase to upstream v1.3.2 version
- Sync specfile with Fedora's version

* Thu Mar 28 2019 Bruno E. O. Meneguele <bmeneg@redhat.com> - 1.1-5
- Add patch to correctly handle key description on keyring during importation

* Mon Oct 29 2018 Bruno E. O. Meneguele <bmeneg@redhat.com> - 1.1-4
- Solve a single memory leak not handled by the last patch

* Thu Oct 25 2018 Bruno E. O. Meneguele <bmeneg@redhat.com> - 1.1-3
- Solve memory leaks pointed by covscan tool
- Add optimization flag O2 during compilation to satisfy annocheck tool

* Fri Mar 02 2018 Bruno E. O. Meneguele <brdeoliv@redhat.com> - 1.1-2
- Remove libtool files
- Run ldconfig scriptlets after un/installing
- Add -devel subpackage to handle include files and examples
- Disable any static file in the package

* Fri Feb 16 2018 Bruno E. O. Meneguele <brdeoliv@redhat.com> - 1.1-1
- New upstream release
- Support for OpenSSL 1.1 was added directly to the source code in upstream,
  thus removing specific patch for it
- Docbook xsl stylesheet updated to a local path

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Feb 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.0-4
- Switch to %%ldconfig_scriptlets

* Fri Dec 01 2017 Bruno E. O. Meneguele <brdeoliv@redhat.com> - 1.0-3
- Add OpenSSL 1.1 API support for the package, avoiding the need of
  compat-openssl10-devel package

* Mon Nov 20 2017 Bruno E. O. Meneguele <brdeoliv@redhat.com> - 1.0-2
- Adjusted docbook xsl path to match the correct stylesheet
- Remove only *.la files, considering there aren't any *.a files

* Tue Sep 05 2017 Bruno E. O. Meneguele <brdeoliv@redhat.com> - 1.0-1
- New upstream release
- Add OpenSSL 1.0 compatibility package, due to issues with OpenSSL 1.1
- Remove libtool files
- Run ldconfig after un/installation to update *.so files
- Add -devel subpackage to handle include files and examples

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.9-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 26 2016 Lubomir Rintel <lkundrak@v3.sk> - 0.9-3
- Fix FTBFS

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Oct 31 2014 Avesh Agarwal <avagarwa@redhat.com> - 0.9-1
- New upstream release
- Applied a patch to fix man page issues.
- Updated spec file

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Aug 27 2013 Vivek Goyal <vgoyal@redhat.com> - 0.6-1
- Initial package
