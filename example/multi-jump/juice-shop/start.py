from sys import argv

import yaml

yaml.Dumper.ignore_aliases = lambda self, data: True


def generate_yaml(n_normal: int, n_attack: int) -> None:
    basic_config = {
        # "image": "juice-shop-bot:latest",
        "environment": {"DEBUG": True},
        "build": {"context": "${CONTEXT_PATH:-.}/bot"},
        "depends_on": ["server"],
    }
    normal_config = basic_config.copy()
    attack_config = {"environment": {"DEBUG": True, "attack": True}, **basic_config}
    attack_config["environment"]["attack"] = True

    services = {}

    steps = []

    for i in range(n_normal):
        name = f"bot-normal-{i}"
        conf = normal_config.copy()
        conf["environment"]["self_host"] = f"192.168.123.{i + 2}"
        conf["environment"]["host_port"] = f"192.168.123.{n_normal + n_attack + 2}:3000"
        conf["container_name"] = name
        conf["networks"] = {
            "subnet": {
                "ipv4_address": f"192.168.123.{i + 2}",
            }
        }

        services[name] = conf

        steps.append(
            {
                "name": name,
                "service": name,
                "command": [
                    "poetry",
                    "run",
                    "python",
                    "main.py",
                ],
                "blocking": False,
            }
        )

    attack_conns = []

    for i in range(n_attack):
        name = f"bot-attack-{i}"
        conf = attack_config.copy()
        conf["environment"]["self_host"] = f"192.168.123.{i + 2 + n_normal}"
        conf["environment"]["host_port"] = f"192.168.123.{n_normal + n_attack + 2}:3000"
        conf["container_name"] = name
        conf["networks"] = {
            "subnet": {
                "ipv4_address": f"192.168.123.{i + 2 + n_normal}",
            }
        }
        services[name] = conf

        steps.append(
            {
                "name": name,
                "service": name,
                "command": [
                    "poetry",
                    "run",
                    "python",
                    "main.py",
                ],
                "blocking": True,
                "is_attack": True,
            }
        )

        attack_conns.append(f"192.168.123.{i + 2 + n_normal}:8888")

    """
    steps.append(
        {
            "name": "server",
            "service": "server",
            "command": [
                "sleep",
                "60",
            ],
            "blocking": True,
        }
    )
    """

    services["server"] = {
        "build": {"context": "${CONTEXT_PATH:-.}"},
        # "image": "juice-shop",
        "ports": ["3000:3000"],
        "networks": {
            "subnet": {
                "ipv4_address": f"192.168.123.{n_normal + n_attack + 2}",
            }
        },
        "x-app-log": "/applog",
    }

    networks = {
        "subnet": {
            "driver": "bridge",
            "ipam": {"config": [{"subnet": "192.168.123.0/24"}]},
        }
    }

    with open("scene.yml", "w") as f:
        yaml.dump(
            {
                "services": services,
                "networks": networks,
                "x-steps": steps,
                "x-attack-conns": attack_conns,
            },
            f,
        )


if __name__ == "__main__":
    n_normal, n_attack = int(argv[1]), int(argv[2])
    generate_yaml(n_normal, n_attack)
    # os.system("docker compose down --remove-orphans; docker compose up -d")
