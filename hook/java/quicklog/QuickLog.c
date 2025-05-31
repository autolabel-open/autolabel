#include <jni.h>
// #include "QuickLog.h"
#include "LoggingAgent_RunnableAdvice.h"
#include "LoggingAgent_CallableAdvice.h"
#include "LoggingAgent_ConstructorAdvice.h"
#include "LoggingAgent_TomcatSocketWrapperBaseAdvice.h"
#include "LoggingAgent_TomcatSocketProcessorBaseAdvice.h"

#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>


JNIEXPORT void JNICALL Java_LoggingAgent_00024TomcatSocketWrapperBaseAdvice_log(JNIEnv *env, jobject obj, jstring string) {
    static int dev_null_file = -1;

    if (dev_null_file == -1) {
        dev_null_file = open("/dev/null", O_WRONLY);
        if (dev_null_file == -1) {
            perror("Failed to open /dev/null");
            exit(EXIT_FAILURE);
        }
    }

    const char *str = (*env)->GetStringUTFChars(env, string, 0);

    write(dev_null_file, str, strlen(str));

    (*env)->ReleaseStringUTFChars(env, string, str);
}

JNIEXPORT void JNICALL Java_LoggingAgent_00024TomcatSocketProcessorBaseAdvice_log(JNIEnv *env, jobject obj, jstring string) {
    static int dev_null_file = -1;

    if (dev_null_file == -1) {
        dev_null_file = open("/dev/null", O_WRONLY);
        if (dev_null_file == -1) {
            perror("Failed to open /dev/null");
            exit(EXIT_FAILURE);
        }
    }

    const char *str = (*env)->GetStringUTFChars(env, string, 0);

    write(dev_null_file, str, strlen(str));

    (*env)->ReleaseStringUTFChars(env, string, str);
}


JNIEXPORT void JNICALL Java_LoggingAgent_00024RunnableAdvice_log(JNIEnv *env, jobject obj, jstring string) {
    static int dev_null_file = -1;

    if (dev_null_file == -1) {
        dev_null_file = open("/dev/null", O_WRONLY);
        if (dev_null_file == -1) {
            perror("Failed to open /dev/null");
            exit(EXIT_FAILURE);
        }
    }

    const char *str = (*env)->GetStringUTFChars(env, string, 0);

    write(dev_null_file, str, strlen(str));

    (*env)->ReleaseStringUTFChars(env, string, str);
}

JNIEXPORT void JNICALL Java_LoggingAgent_00024CallableAdvice_log(JNIEnv *env, jobject obj, jstring string) {
    static int dev_null_file = -1;

    if (dev_null_file == -1) {
        dev_null_file = open("/dev/null", O_WRONLY);
        if (dev_null_file == -1) {
            perror("Failed to open /dev/null");
            exit(EXIT_FAILURE);
        }
    }

    const char *str = (*env)->GetStringUTFChars(env, string, 0);

    write(dev_null_file, str, strlen(str));

    (*env)->ReleaseStringUTFChars(env, string, str);
}

JNIEXPORT void JNICALL Java_LoggingAgent_00024ConstructorAdvice_log(JNIEnv *env, jobject obj, jstring string) {
    static int dev_null_file = -1;

    if (dev_null_file == -1) {
        dev_null_file = open("/dev/null", O_WRONLY);
        if (dev_null_file == -1) {
            perror("Failed to open /dev/null");
            exit(EXIT_FAILURE);
        }
    }

    const char *str = (*env)->GetStringUTFChars(env, string, 0);

    write(dev_null_file, str, strlen(str));

    (*env)->ReleaseStringUTFChars(env, string, str);
}
