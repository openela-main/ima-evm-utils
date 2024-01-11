%bcond_with compat

# For cases where the soname requires a bump we need to define with_compat,
# update the package into the side-tag, update RPM (rpm-sign) into side-tag,
# _then_ undefine with_compat and rebuild the package into the side-tag. This
# is required to workaround the chiken-egg situation with the rpm-sign update.
# The compat pkg must not make the compose, it's only a buildrequirement for
# rpm-sign in a soname bump.
%if ! %{with compat}
%undefine with_compat
%endif

%if %{with compat}
%global compat_soversion 2
%endif

Name:    ima-evm-utils
Version: 1.4
Release: 4%{?dist}
Summary: IMA/EVM support utilities
License: GPLv2
Url:     http://linux-ima.sourceforge.net/
Source:  http://sourceforge.net/projects/linux-ima/files/ima-evm-utils/%{name}-%{version}.tar.gz

# compat source and patches
Source10: ima-evm-utils-1.3.2.tar.gz
Patch10:  0001-evmctl-fix-memory-leak-in-get_password.patch
Patch11:  0001-libimaevm-make-SHA-256-the-default-hash-algorithm.patch

BuildRequires: asciidoc
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gcc
BuildRequires: keyutils-libs-devel
BuildRequires: libtool
BuildRequires: libxslt
BuildRequires: make
BuildRequires: openssl-devel
BuildRequires: tpm2-tss-devel

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

%if %{with compat}
%package -n %{name}%{compat_soversion}
Summary: Compatibility package of %{name}

%description -n %{name}%{compat_soversion}
This package provides the libimaevm.so.%{compat_soversion} relative to %{name}-1.3
%endif

%prep
%setup -q

%if %{with compat}
mkdir compat/
tar -zxf %{SOURCE10} --strip-components=1 -C compat/
cd compat/
%patch10 -p1
%patch11 -p1
%endif

%build
autoreconf -vif
%configure --disable-static
%make_build

%if %{with compat}
pushd compat/
autoreconf -vif
%configure --disable-static
%make_build
popd
%endif

%install
%make_install
find %{buildroot} -type f -name "*.la" -print -delete

%if %{with compat}
pushd compat/src/.libs/
install -p libimaevm.so.%{compat_soversion}.0.0 %{buildroot}%{_libdir}/libimaevm.so.%{compat_soversion}.0.0
ln -s -f %{buildroot}%{_libdir}/libimaevm.so.%{compat_soversion}.0.0 %{buildroot}%{_libdir}/libimaevm.so.%{compat_soversion}
popd
%endif

%ldconfig_scriptlets

%files
%license COPYING
%doc NEWS README AUTHORS
%{_bindir}/evmctl
# if you need to bump the soname version, coordinate with dependent packages
%{_libdir}/libimaevm.so.3*
%{_mandir}/man1/evmctl*

%files devel
%{_pkgdocdir}/*.sh
%{_includedir}/imaevm.h
%{_libdir}/libimaevm.so

%if %{with compat}
%files -n %{name}%{compat_soversion}
%{_libdir}/libimaevm.so.%{compat_soversion}
%{_libdir}/libimaevm.so.%{compat_soversion}.0.0
%endif

%changelog
* Mon Dec 13 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.4-4
- Fix compat bcond_with value check.

* Fri Dec 10 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.4-3
- Remove compat subpkg from compose (rhbz#2026028)

* Tue Dec 07 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.4-2
- Add compat subpkg for helping building dependencies (rhbz#2026028)

* Thu Dec 02 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.4-1
- Modify some pieces to get closer to Fedora's specfile
- Remove patch handling memory leak: solved in the rebase
- Remove patch handling SHA-256 default hash: solved in the rebase
- Rebase to upstream release v1.4 (rhbz#2026028)

* Fri Aug 20 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-9
- Use upstream accepted patch for the memory leak
- Make SHA-256 the default hash algorithm (rhbz#1934949)

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.3.2-6
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Jul 08 2021 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-5
- Add patch fixing memory leak (rhbz#1938742)

* Wed Jun 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.3.2-4
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.3.2-3
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Oct 28 2020 Bruno Meneguele <bmeneg@redhat.com> - 1.3.2-1
- Rebase to new upstream v1.3.2 minor release

* Tue Aug 11 2020 Bruno Meneguele <bmeneg@redhat.com> - 1.3.1-1
- Rebase to new upstream v1.3.1 minor release

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun Jul 26 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 1.3-2
- Fix devel deps

* Sun Jul 26 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 1.3-1
- Update to 1.3
- Use tpm2-tss instead of tss2
- Minor spec cleanups

* Mon Jul 13 2020 Tom Stellard <tstellar@redhat.com> - 1.2.1-4
- Use make macros
- https://fedoraproject.org/wiki/Changes/UseMakeBuildInstallMacro

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jul 31 2019 Bruno E. O. Meneguele <bmeneg@redhat.com> - 1.2.1-2
- Add pull request to correct lib soname version, wich was bumped to 1.0.0

* Wed Jul 31 2019 Bruno E. O. Meneguele <bmeneg@redhat.com> - 1.2.1-1
- Rebase to upstream v1.2.1
- Remove both patches that were already solved in upstream version
- Add runtime dependency of tss2 to retrieve PCR bank data from TPM2.0

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 20 2018 Bruno E. O. Meneguele <brdeoliv@redhat.com> - 1.1-4
- Add patch to remove dependency from libattr-devel package

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

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
