obj-m += filter_$(INSTANCE).o

all: check_params filter.h
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

filter.h: check_params config_filter.py configure.py
	python_executable=$(python_executable) $(python_executable) configure.py $(INSTANCE)

check_params:
ifndef INSTANCE
  $(error INSTANCE is not set)
endif

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
	-rm *~
	-rm filter.h
