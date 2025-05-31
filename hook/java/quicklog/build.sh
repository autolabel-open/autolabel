export JAVA_HOME="/usr/lib/jvm/java-1.8.0-openjdk-amd64"
gcc -shared -fpic -o libquicklog.so -I${JAVA_HOME}/include -I${JAVA_HOME}/include/linux QuickLog.c
