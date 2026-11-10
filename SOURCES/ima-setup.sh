#!/bin/bash
#
# This script helps set up IMA.
#
IMA_SYSTEMD_POLICY=/etc/ima/ima-policy
IMA_POLICY_SYSFS=/sys/kernel/security/ima/policy

usage() {
	echo "Set up IMA."
	cat <<EOF
usage: $0 --policy=IMA_POLICY_PATH [--reinstall_threshold=NUM]

       --policy
       The path of IMA policy to be loaded. Sample polices are inside
       /usr/share/ima/policies or you can use your own IMA policy

       --reinstall_threshold
       By default, IMA sigatures will be obtained from the RPM DB. However the
       RPM DB may not have the signatures. Dectect this case by checking if
       there are >reinstall_threshold package missing IMA signatures and
       reinstall them.

EOF
	exit 1
}

for _opt in "$@"; do
	case "$_opt" in
	--policy=*)
		ima_policy_path=${_opt#*=}
		if [[ ! -r $ima_policy_path ]]; then
			echo "$ima_policy_path doesn't exist"
			exit 1
		fi
		;;
	--reinstall_threshold=*)
		reinstall_threshold=${_opt#*=}
		;;
	*)
		usage
		;;
	esac
done

if [[ $# -eq 0 ]]; then
	usage
fi

# Check for required argument
if [[ "$ima_policy_path" == "" ]]; then
	echo "No policy file was given"
	echo
	usage
	exit 1
fi

if ! rpm --quiet -q rpm-plugin-ima; then
	echo "Installing prerequisite package rpm-plugin-ima"
	if ! dnf install rpm-plugin-ima -yq; then
		echo "Failed to install rpm-plugin-ima, abort"
		exit 1
	fi
fi

# Add IMA signatures
if test -f /run/ostree-booted; then
	echo "You are using OSTree, please enable IMA signatures as part of the OSTree creation process."
else
	echo "Adding IMA signatures to installed package files"
	if ! ima-add-sigs --reinstall_threshold="$reinstall_threshold"; then
		echo "Failed to add IMA signatures, abort"
		exit 1
	fi
fi

load_ima_keys() {
	local _key_loaded

	if line=$(keyctl describe %keyring:.ima); then
		_ima_id=${line%%:*}
	else
		echo "Failed to get ID of the .ima  keyring"
		exit 1
	fi

	for i in /etc/keys/ima/*; do
		if [ ! -f "${i}" ]; then
			echo "No IMA key exist"
			exit 1
		fi

		if ! evmctl import "${i}" "${_ima_id}" &>/dev/null; then
			echo "Failed to load IMA key ${i}"
		else
			_key_loaded=yes
		fi
	done

	if [[ $_key_loaded != yes ]]; then
		echo "No IMA key loaded"
		exit 1
	fi
}

load_ima_policy() {
	local ima_policy_path

	ima_policy_path=$1

	if ! echo "$ima_policy_path" >"$IMA_POLICY_SYSFS"; then
		echo "$ima_policy_path can't be loaded"
		return 1
	fi
	# Let systemd load the IMA policy which will load LSM rules first so IMA
	# policy containing rules like "appraise obj_type=ifconfig_exec_t" can be
	# loaded
	[[ -e /etc/ima ]] || mkdir -p /etc/ima/
	if ! cp --preserve=all "$ima_policy_path" "$IMA_SYSTEMD_POLICY"; then
		echo "Failed to copy $ima_policy_path to $IMA_SYSTEMD_POLICY"
		return 1
	fi
}

echo "Loading IMA keys"
load_ima_keys

# Include the dracut integrity module to load the IMA keys and policy
# automatically when there is a system reboot
if ! lsinitrd --mod | grep -q integrity; then
	cp --preserve=all /usr/share/ima/dracut-98-integrity.conf /etc/dracut.conf.d/98-integrity.conf
	echo "Regenerating all initramfs images to include the dracut integrity module"
	if ! dracut -f --regenerate-all; then
		echo "Failed to Regenerate all initramfs images"
		exit 1
	fi
	[[ $(uname -m) == s390x ]] && zipl &> /dev/null
fi

if ! load_ima_policy "$ima_policy_path"; then
	echo "Failed to load IMA policy $ima_policy_path!"
	exit 1
fi
