public class LoggingAgent {
    public static class TomcatSocketWrapperBaseAdvice {
        public static native void log(String message);
    }
    public static class TomcatSocketProcessorBaseAdvice {
        public static native void log(String message);
    }
    public static class CallableAdvice {
        public static native void log(String message);
    }
    public static class RunnableAdvice {
        public static native void log(String message);
    }
    public static class ConstructorAdvice {
        public static native void log(String message);
    }
}
