import net.bytebuddy.agent.builder.AgentBuilder;
import net.bytebuddy.asm.Advice;
import java.lang.instrument.Instrumentation;
import java.lang.reflect.Field;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;

import static net.bytebuddy.matcher.ElementMatchers.*;

public class LoggingAgent {

    public static void premain(String agentArgs, Instrumentation inst) {
        new AgentBuilder.Default()
            // .with(AgentBuilder.Listener.StreamWriting.toSystemOut())
            .type(isSubTypeOf(Callable.class))
            .transform((builder, typeDescription, classLoader, module) ->
                builder
                    .method(named("call"))
                    .intercept(Advice.to(CallableAdvice.class))
                    .constructor(any())
                    .intercept(Advice.to(ConstructorAdvice.class))
            )
            .type(isSubTypeOf(Runnable.class).and(not(nameContains("SocketProcessorBase"))))
            .transform((builder, typeDescription, classLoader, module) ->
                //System.out.println("Transforming Runnable: " + typeDescription.getName());
                builder
                    .method(named("run"))
                    .intercept(Advice.to(RunnableAdvice.class))
                    .constructor(any())
                    .intercept(Advice.to(ConstructorAdvice.class))
            )
            .type(nameContains("SocketWrapperBase"))
            .transform((builder, typeDescription, classLoader, module) ->
                builder
                    .constructor(any())
                    .intercept(Advice.to(TomcatSocketWrapperBaseAdvice.class))
            )
            .type(nameContains("SocketProcessorBase"))
            .transform((builder, typeDescription, classLoader, module) ->
                builder
                    .method(named("run"))
                    .intercept(Advice.to(TomcatSocketProcessorBaseAdvice.class))
            )
            .installOn(inst);
    }

    public static class TomcatSocketWrapperBaseAdvice {
        static {
            System.loadLibrary("quicklog");
        }
        public static native void log(String message);

        @Advice.OnMethodExit
        public static void enter(@Advice.This(optional = true) Object obj) {
            if (obj != null)
                log("JV_CREATE " + System.identityHashCode(obj) + "SocketWrapperBase");
        }
    }


    public static class TomcatSocketProcessorBaseAdvice {
        static {
            System.loadLibrary("quicklog");
        }
        public static native void log(String message);

        public static final ConcurrentHashMap<Class<?>, Field> fieldCache = new ConcurrentHashMap<>();

        public static Field cacheField(Class<?> clazz, String fieldName) {
            if (fieldCache.containsKey(clazz)) {
                return fieldCache.get(clazz);
            }
            Class<?> current = clazz;
            while (current != null) {
                try {
                    Field field = current.getDeclaredField(fieldName);
                    field.setAccessible(true);  // Make sure the field is accessible
                    fieldCache.put(clazz, field);
                    return field;
                } catch (NoSuchFieldException e) {
                    current = current.getSuperclass();
                }
            }
            fieldCache.put(clazz, null);
            return null;
        }

        @Advice.OnMethodEnter
        public static void enter(@Advice.This(optional = true) Object obj) {
            if (obj != null) {
                try {
                    Field field = cacheField(obj.getClass(), "socketWrapper");
                    if (field == null) return;
                    Object socketWrapper = field.get(obj);
                    log("JV_RUN_START " + System.identityHashCode(socketWrapper) + "SocketWrapperBase");
                } catch (Exception e) {
                    log("ERROR_JV " + e.toString());
                }
            }
        }

        @Advice.OnMethodExit
        public static void exit(@Advice.This(optional = true) Object obj) {
            if (obj != null) {
                try {
                    Field field = cacheField(obj.getClass(), "socketWrapper");
                    if (field == null) return;
                    Object socketWrapper = field.get(obj);
                    log("JV_RUN_END " + System.identityHashCode(socketWrapper) + "SocketWrapperBase");
                } catch (Exception e) {
                    log("ERROR_JV " + e.toString());
                }
            }
        }

        /*
        @Advice.OnMethodExit
        public static void exit(@Advice.This(optional = true) Object obj, @Advice.Origin("#t") String className) {
            if (obj != null)
                log("JV_TOMCAT_END " + System.identityHashCode(obj) + className);

        }
        */
    }

    public static class RunnableAdvice {
        static {
            System.loadLibrary("quicklog");
        }
        public static native void log(String message);

        @Advice.OnMethodEnter
        public static void enter(@Advice.This(optional = true) Object obj, @Advice.Origin("#t") String className) {
            if (obj != null)
                log("JV_RUN_START " + System.identityHashCode(obj) + className);
        }


        @Advice.OnMethodExit
        public static void exit(@Advice.This(optional = true) Object obj, @Advice.Origin("#t") String className) {
            if (obj != null)
                log("JV_RUN_END " + System.identityHashCode(obj) + className);

        }
    }

    public static class CallableAdvice {
        static {
            System.loadLibrary("quicklog");
        }

        public static native void log(String message);

        @Advice.OnMethodEnter
        public static void enter(@Advice.This(optional = true) Object obj, @Advice.Origin("#t") String className) {
            if (obj != null)
                log("JV_CALL_START " + System.identityHashCode(obj) + className);
        }


        @Advice.OnMethodExit
        public static void exit(@Advice.This(optional = true) Object obj, @Advice.Origin("#t") String className) {
            if (obj != null)
                log("JV_CALL_END " + System.identityHashCode(obj) + className);
        }
    }

    public static class ConstructorAdvice {
        static {
            System.loadLibrary("quicklog");
        }

        public static native void log(String message);

        @Advice.OnMethodExit
        public static void enter(@Advice.This(optional = true) Object obj, @Advice.Origin("#t") String className) {
            if (obj != null)
                log("JV_CREATE " + System.identityHashCode(obj) + className);
        }
    }
}