from sys import argv

import yaml

yaml.Dumper.ignore_aliases = lambda self, data: True


def generate_yaml(n_normal: int, n_attack: int) -> None:
    basic_config = {
        "image": "juice-shop-bot:latest",
        "depends_on": ["server"],
    }
    normal_config = basic_config.copy()
    attack_config = {"environment": ["attack=True"], **basic_config}

    services = {}
    for i in range(n_normal):
        name = f"bot-normal-{i}"
        conf = normal_config.copy()
        conf["environment"] = [f"self_host={name}"]
        services[name] = conf
    for i in range(n_attack):
        name = f"bot-attack-{i}"
        conf = attack_config.copy()
        conf["environment"] += [f"self_host={name}"]
        services[name] = conf

    with open("bots.yml", "w") as f:
        yaml.dump({"services": services}, f)


if __name__ == "__main__":
    n_normal, n_attack = int(argv[1]), int(argv[2])
    generate_yaml(n_normal, n_attack)
    # os.system("docker compose down --remove-orphans; docker compose up -d")
