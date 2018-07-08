#add the google apt-key to the keystore
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

#install the kubernetes repo for xenial
cat <<EOF > /etc/apt/sources.list.d/kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF

#make sure the package cache is up to date
apt-get update

#install some extra packages for Docker

apt install linux-image-extra-virtual ca-certificates curl software-properties-common -y

# Install the docker apt key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

#Add Docker repo to apt
add-apt-repository    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) \
stable"

#Update the package cache agian
apt-get update

#install all needed packages

apt-get install docker-ce=$(apt-cache madison docker-ce | grep 17.03 | head -1 | awk '{print $3}') kubelet kubeadm kubectl kubernetes-cni -y
