# -*- mode: ruby -*-
# vi: set ft=ruby :
$script = <<SCRIPT

echo Installing depedencies...
sudo apt-get update
sudo apt-get install -y build-essential python-pip redis-server automake r-base python-dev libtool
sudo pip install -U pip

#InsecurePlatformWarning
sudo pip install --upgrade requests[security]

#install project dependencies
sudo pip install -r /opt/anna-molly/requirements.txt

SCRIPT

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.provision "shell", inline: $script
  config.vm.network "private_network", type: 'dhcp'
  config.vm.synced_folder '.', '/opt/anna-molly'
  config.vm.hostname = "anna-molly"
end
