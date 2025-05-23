# #
## Copyright (c) 2019 Matthias Tafelmeier
##
## This file is part of godon
##
## godon is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## godon is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with godon. If not, see <http://www.gnu.org/licenses/>.
##

{ config, pkgs, lib, ... }:

{
  imports = [ ./hardware-configuration.nix ];

  boot = {
    loader = { grub.enable = true; };
    kernelPackages = pkgs.linuxPackages_6_12;
  };

  services = {
    openssh.enable = true;
    github-runners.gh-runner = {
      enable = true;
      url = "https://github.com/godon-dev";
      tokenFile = "/srv/gh_runner.token";
      extraLabels = [ "nixos" "osuosl" ];
      extraPackages = with pkgs; [ nixos-generators mask kind kubernetes-helm docker docker-compose iproute2 jq yq-go ];
      workDir = "/github-runner/";
      serviceOverrides = {
        PrivateUsers = false;
        DynamicUser = false;
        PrivateDevices = false;
        PrivateMounts = false;
        AmbientCapabilities = [ "CAP_NET_ADMIN" ];
        CapabilityBoundingSet = [ "CAP_NET_ADMIN" ];
      };
    };
  };

  # create github-runner work dir
  systemd.tmpfiles.rules = [ "d /github-runner/ 0755 root root -" "d /github-runner/artifacts 0755 root root -" ];
  # override docker limits
  systemd.services.docker.serviceConfig = { LimitNOFILE=4194304; };

  environment.systemPackages = let
    pythonModules = pythonPackages: with pythonPackages; [ pyyaml ];
  in with pkgs; [
    (python3.withPackages pythonModules)
    ansible
    bashInteractive_5
    cargo
    clang
    ctags
    curl
    docker
    docker-compose
    ethtool
    git
    git-crypt
    gnupg
    htop
    iperf3
    iproute2
    jq
    yq-go
    killall
    kind
    kubernetes-helm
    mask
    nmap
    nixos-generators
    openssh
    parted
    pciutils
    rsync
    tcpdump
    tcpflow
    traceroute
    tree
    unzip
    util-linux
    wget
    vim
  ];

  users.users.godon = {
    isNormalUser = true;
    home = "/home/godon/";
    extraGroups = [ "wheel" "docker" "libvirtd" ];
    openssh.authorizedKeys.keys = [
      "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDLt7w6tl++WJT/Bn1HsOep25KpgL867SuZAnK5ifOgd6wS0PxHGiCD/4A0RSHdHZTXMv37DGlC36rhlWJUdsncI5O1F5Ay2d626fPg+REaGi8R7Hox/qInkDs9/NS2IbZvQaYIdeDK151McagWijRFCxTEMYftpslXWKiN5ckP/KjFdUkS7fKcGwqk+UFy7ehMF42i8MUOdkZMJwy8Yc2y4FTdzlrh8VELkMxCePcU9LrvwY5sSh9j65Q5IcIBlma36JMJZQLuEWi7oEGAASehUNeMXs9WFkbyCCWdR1PjHNfbrgZUpgw71SkiQrM8+9/jcfyl5kfkn+GUECQcWBDQnbi809re1ZVmOSUrDBAoEAevFO8qHLgz0d9H0Zs/EOghyN+a4eBLB3et46F733GYGGO4AMMvRSibeyHCLINCLeV19FkHXSxD5iXTRt6WXo3vhKC/tw0XN0yNSOc1nHC+azAJxG6zOxzUzXjC9c1wxaWmGReeanlefQTHVRcMtBfm1NAOwaD0DubSTEBeRRMHfW2ZRs3nV0l73HJWh9J8+5MTpCOK7BGzC0LILMsSqpltUTLI3YmFO5Ly9RokUbcFmnn4Yu4IreTITMmn73CuLNkjZIKwucWmJkWNmWc1hrLRO12Yad/aQS+rczKcQFoNXl+bBmIAOWYJ1C6mSKG/Hw== ci_runner@gh"
    ];
  };

  users.users.github-runner-nixos = {
    isNormalUser = true;
    home = "/home/github-runner-nixos/";
    extraGroups = [ "wheel" "docker" "libvirtd" "systemd-network" ];
    openssh.authorizedKeys.keys = [
      "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDLt7w6tl++WJT/Bn1HsOep25KpgL867SuZAnK5ifOgd6wS0PxHGiCD/4A0RSHdHZTXMv37DGlC36rhlWJUdsncI5O1F5Ay2d626fPg+REaGi8R7Hox/qInkDs9/NS2IbZvQaYIdeDK151McagWijRFCxTEMYftpslXWKiN5ckP/KjFdUkS7fKcGwqk+UFy7ehMF42i8MUOdkZMJwy8Yc2y4FTdzlrh8VELkMxCePcU9LrvwY5sSh9j65Q5IcIBlma36JMJZQLuEWi7oEGAASehUNeMXs9WFkbyCCWdR1PjHNfbrgZUpgw71SkiQrM8+9/jcfyl5kfkn+GUECQcWBDQnbi809re1ZVmOSUrDBAoEAevFO8qHLgz0d9H0Zs/EOghyN+a4eBLB3et46F733GYGGO4AMMvRSibeyHCLINCLeV19FkHXSxD5iXTRt6WXo3vhKC/tw0XN0yNSOc1nHC+azAJxG6zOxzUzXjC9c1wxaWmGReeanlefQTHVRcMtBfm1NAOwaD0DubSTEBeRRMHfW2ZRs3nV0l73HJWh9J8+5MTpCOK7BGzC0LILMsSqpltUTLI3YmFO5Ly9RokUbcFmnn4Yu4IreTITMmn73CuLNkjZIKwucWmJkWNmWc1hrLRO12Yad/aQS+rczKcQFoNXl+bBmIAOWYJ1C6mSKG/Hw== ci_runner@gh"
    ];
  };

  virtualisation = {
    docker.enable = true;
    vswitch.enable = true;
    libvirtd = {
      enable = true;
      onShutdown = "shutdown";
    };
  };

  ## Required for kind cluster to work network wise
  networking.firewall.checkReversePath = "loose";

  security = {
    sudo.wheelNeedsPassword = false; # for automatic use
    polkit = { enable = true; };
    pam.loginLimits = [
      {
        domain = "*";
        type = "soft";
        item = "nofile";
        value = "4194304";
      }
      {
        domain = "*";
        type = "hard";
        item = "nofile";
        value = "4194304";
      }
    ];
  };

  nixpkgs.config.allowUnfree = true;

  system.nixos.version = "24.05";
}
