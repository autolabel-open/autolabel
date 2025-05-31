clean:
	rm -f hook_glibc_attacker.so # ip_list.h

# ip_list.h: configure.py config_attack.py
# 	python configure.py

hook_glibc_attacker.so: hook_glibc_attacker.c ip_list.h
	gcc -shared -fPIC -o hook_glibc_attacker.so hook_glibc_attacker.c -ldl
