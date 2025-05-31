obj-m += write_uuid_$(INSTANCE).o

all: check_params write_uuid.h
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

write_uuid.h: config_applog.py configure.py write_uuid.c
	python configure.py $(INSTANCE)

check_params:
ifndef INSTANCE
	$(error INSTANCE is not set)
endif

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
	-rm *~
	-rm write_uuid.h
