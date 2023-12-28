%bcond_without python3

%global pkgname oath

Summary:          Python implementation of HOTP, TOTP and OCRA
Name:             python-%{pkgname}
Version:          1.4.3
Release:          CROC2_REDOS_TEST1%{?dist}
License:          BSD 3-clause
Group:            Development/Libraries

Provides:         %name = %version-%release
BuildRequires:    make

URL:              https://github.com/bdauvergne/python-oath
BuildArch:        noarch

Vendor:           Benjamin Dauvergne <bdauvergne@entrouvert.com>

Source0:          %name-%version.tar.gz

%global _description\
Python implementation of the three main OATH specifications: HOTP, TOTP and OCRA

%description %_description


%if %{with python3}
%package -n python%{python3_pkgversion}-%{pkgname}
Summary:        %summary

BuildRequires:  python%{python3_pkgversion}
BuildRequires:  python%{python3_pkgversion}-setuptools

%description -n python%{python3_pkgversion}-%{pkgname} %_description
%endif


%prep
%setup -n %name-%version -q


%build
%py3_build



%install
[ %buildroot = "/" ] || rm -rf %buildroot
%py3_install



%check
%{__python3} setup.py test


%clean
rm -rf %{buildroot}



%files -n python%{python3_pkgversion}-%{pkgname}
%doc README.rst
%{python3_sitelib}/*


%changelog
* Mon Apr 13 2020 Croc Cloud Engineering - 1.4.3-CROC1
- Build for py2/py3 for Croc cloud
