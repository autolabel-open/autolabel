const async_hooks = require("async_hooks");
const native = require("./build/Release/async_hook.node");

const hook = async_hooks.createHook({
    init(asyncId, type, triggerAsyncId) {
        native.initHook(asyncId, type, triggerAsyncId);
    },
    before(asyncId) {
        native.beforeHook(asyncId);
    },
    after(asyncId) {
        native.afterHook(asyncId);
    },
});

hook.enable();

// setTimeout(() => {
//     console.log("timeout executed");
// }, 100);

// console.log("happy new year");
