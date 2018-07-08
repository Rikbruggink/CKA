#install headers
apt-get -y install linux-headers-$(uname -r) build-essential dkms perl

# Mount the disk image
cd /tmp
mkdir /tmp/isomount
mount -t iso9660 -o loop /root/VBoxGuestAdditions_$(cat /root/.vbox_version).iso /tmp/isomount

# Install the drivers
/tmp/isomount/VBoxLinuxAdditions.run

# Cleanup
umount isomount
