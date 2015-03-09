# -*- mode: ruby -*-
# vi: set ft=ruby :
$script = <<SCRIPT

echo Installing depedencies...
sudo apt-get update
sudo apt-get install -y build-essential python-pip redis-server automake r-base python-dev libtool
sudo pip install -r /opt/anna-molly/requirements.txt

SCRIPT

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "hashicorp/precise64"

  config.vm.provision "shell", inline: $script

  config.vm.define "n1" do |n1|
      n1.vm.network "private_network", ip: "172.20.20.10"
  end

  config.vm.synced_folder '.', '/opt/anna-molly'

  config.vm.hostname = "anna-molly"

end