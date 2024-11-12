#!/bin/bash
#
# This script add IMA signatures to installed RPM package files
# Usage: add_ima_sigs.sh [--package=PACKAGE_NAME|ALL] [--ima-cert=IMA_CERT_PATH] [--reinstall_threshold=NUM]
#
# By default, it will add IMA sigantures to all installed package files. Or you
# can provide a package name to only add IMA signature for files of specicifed
# package.  If it detects >=20 packages (or 1 package if you specify a package
# name) missing signatures in the RPM database, it will reinstall the packages
# in order to get the IMA signatures.
#
# With the signing IMA cert path specified, it will also try to verify
# the added IMA signature.

for _opt in "$@"; do
	case "$_opt" in
	--reinstall_threshold=*)
		reinstall_threshold=${_opt#*=}
		;;
	--package=*)
		package=${_opt#*=}
		;;
	--ima_cert=*)
		ima_cert=${_opt#*=}
		;;
	*)
		usage
		;;
	esac
done

if [[ -z $package ]] || [[ $package == ALL ]]; then
	package="--all"
fi

abort() {
	echo "$1"
	exit 1
}

# Add IMA signatures from RPM database
add_from_rpm_db() {
	if ! command -v setfattr &>/dev/null; then
			abort "Please install attr"
	fi

	# use "|" as deliminator since it won't be used in a filename or signature
	while IFS="|" read -r path sig; do
		# [[ -z "$sig" ]] somehow doesn't work for some files that don't have IMA
		# signatures. This may be a issue of rpm
		if [[ "$sig" != "0"* ]]; then
			continue
		fi

		# Skip directory, soft links, non-existent files and vfat fs
		if [[ -d "$path" || -L "$path" || ! -f "$path" || "$path" == "/boot/efi/EFI/"* ]]; then
			continue
		fi

		if ! setfattr -n security.ima "$path" -v "0x$sig"; then
			echo "Failed to add IMA sig for $path"
		fi

		[[ -e "$ima_cert" ]] || continue
		# TODO
		# don't verify the modified files like /etc?
		if ! evmctl ima_verify -k "$ima_cert" "$path" &>/dev/null; then
			echo "Failed to verify $path"
		fi
	done < <(rpm -q --queryformat "[%{FILENAMES}|%{FILESIGNATURES}\n]" "$package")
}

# Add IMA signatures by reinstalling all packages
add_by_reinstall() {
	[[ $package == "--all" ]] && package='*'
	dnf reinstall "$package" -yq >/dev/null
}

if [[ -z $reinstall_threshold ]]; then
	if [[ $package == "--all" ]]; then
		reinstall_threshold=20
	else
		if ! rpm -q --quiet $package; then
			dnf install "$package" -yq >/dev/null
			exit 0
		fi
		reinstall_threshold=1
	fi
fi

unsigned_packages_in_rpm_db=$(rpm -q --queryformat "%{SIGPGP:pgpsig}\n" $package | grep "^(none)$" | wc -l)

if [[ $unsigned_packages_in_rpm_db -ge $reinstall_threshold ]]; then
	add_by_reinstall
else
	add_from_rpm_db
fi
