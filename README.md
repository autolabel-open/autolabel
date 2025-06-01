# AutoLabel

This provides the code & documentation & image packages for AutoLabel.

- Zenodo address for code & documentation & image packages: https://doi.org/10.5281/zenodo.15540310
- Zenodo address for pre-generated datasets:
  - Part1: https://doi.org/10.5281/zenodo.15528780
  - Part2: https://doi.org/10.5281/zenodo.15532579
  - Part3: https://doi.org/10.5281/zenodo.15568798
- For details, please refer to https://github.com/autolabel-open/autolabel.

## Scenario Description

Please refer to the documentation: [Scenario Description](./scenario_descriptions.md)

## Install

```bash
poetry install
curl -s https://download.sysdig.com/stable/install-sysdig | sudo bash
sudo apt install tshark conntrack tcpdump
```

## Other Requirements

- Need to ensure vm.max_map_count>=262144.
- Need to set file descriptor soft and hard limits large enough in `/etc/security/limits.conf`.

```
* soft nofile 1048576
* hard nofile 1048576
```

- Since we have packaged many docker images, you need to use `docker load -i` to load the image packages.

```
gzip -d all_images.tar.gz
docker load -i ./all_images.tar
```

## Usage

Refer to `build.sh`.
