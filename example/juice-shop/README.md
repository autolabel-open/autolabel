# Juice Shop 实验

## 启动

执行 `python start.py {x} {y}`，其中 x 为正常 bot 数量，y 为攻击 bot 数量。执行后 docker compose 将会启动 Juice Shop 服务及 x+y 个 bots，bots 会自动开始访问服务，产生数据。

## 参考资料

- POC：[OWASP Juice Shop](https://help.owasp-juice.shop/appendix/solutions.html)
- 主页：https://owasp.org/www-project-juice-shop/