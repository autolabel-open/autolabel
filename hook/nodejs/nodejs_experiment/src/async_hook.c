#include <node_api.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

#include "async_hook.h"

void log_ins_event(const char* typ, const long int ptr) {
  static __thread char buffer[256];
  static int dev_null_file = -1;

  if (dev_null_file == -1) {
    dev_null_file = open("/dev/null", O_WRONLY);
    if (dev_null_file == -1) {
      perror("Failed to open /dev/null");
      exit(EXIT_FAILURE);
    }
  }

  int len = snprintf(buffer, sizeof(buffer), "furina-node-ins %s %ld", typ, ptr);
  write(dev_null_file, buffer, len);
}


// Init钩子处理函数
napi_value InitHook(napi_env env, napi_callback_info info) {
    size_t argc = 3;
    napi_value args[3];
    napi_get_cb_info(env, info, &argc, args, NULL, NULL);

    // 解析参数
    int64_t asyncId, triggerAsyncId;
    char type[256];
    size_t type_len;

    napi_get_value_int64(env, args[0], &asyncId);
    napi_get_value_int64(env, args[1], &triggerAsyncId);
    napi_get_value_string_utf8(env, args[2], type, sizeof(type), &type_len);

    // 在此添加处理逻辑
    log_ins_event("handler_init", asyncId);
    return NULL;
}

// Before钩子处理函数
napi_value BeforeHook(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value args[1];
    napi_get_cb_info(env, info, &argc, args, NULL, NULL);

    int64_t asyncId;
    napi_get_value_int64(env, args[0], &asyncId);

    // 在此添加处理逻辑
    log_ins_event("handler_begin", asyncId);
    return NULL;
}

// After钩子处理函数
napi_value AfterHook(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value args[1];
    napi_get_cb_info(env, info, &argc, args, NULL, NULL);

    int64_t asyncId;
    napi_get_value_int64(env, args[0], &asyncId);

    // 在此添加处理逻辑
    log_ins_event("handler_end", asyncId);

    return NULL;
}

// 模块初始化
napi_value Init(napi_env env, napi_value exports) {
    napi_property_descriptor desc[] = {
        { "initHook", NULL, InitHook, NULL, NULL, NULL, napi_default, NULL },
        { "beforeHook", NULL, BeforeHook, NULL, NULL, NULL, napi_default, NULL },
        { "afterHook", NULL, AfterHook, NULL, NULL, NULL, napi_default, NULL }
    };
    napi_define_properties(env, exports, 3, desc);
    return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
