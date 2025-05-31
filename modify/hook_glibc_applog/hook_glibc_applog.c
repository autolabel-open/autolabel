#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>

typedef FILE *(*orig_fopen_pt)(const char *__restrict __filename,
                               const char *__restrict __modes);

typedef FILE *(*orig_fopen64_pt)(const char *__restrict __filename,
                                 const char *__restrict __modes);

typedef FILE *(*orig_fdopen_pt)(int __fd, const char *__modes);

static orig_fopen_pt orig_fopen_func = NULL;
static orig_fopen64_pt orig_fopen64_func = NULL;
static orig_fdopen_pt orig_fdopen_func = NULL;

FILE *fdopen(int __fd, const char *__modes) {
  if (orig_fdopen_func == NULL) {
    orig_fdopen_func = (orig_fdopen_pt)dlsym(RTLD_NEXT, "fdopen");
  }

  // fprintf(stderr, "there is a fdopen!\n");

  FILE *ret = orig_fdopen_func(__fd, __modes);
  if (ret != NULL)
    setbuf(ret, NULL);

  return ret;
}

FILE *fopen(const char *__restrict __filename, const char *__restrict __modes) {
  if (orig_fopen_func == NULL) {
    orig_fopen_func = (orig_fopen_pt)dlsym(RTLD_NEXT, "fopen");
  }

  // fprintf(stderr, "there is a fopen!\n");

  FILE *ret = orig_fopen_func(__filename, __modes);
  if (ret != NULL)
    setbuf(ret, NULL);

  return ret;
}

FILE *fopen64(const char *__restrict __filename,
              const char *__restrict __modes) {
  if (orig_fopen64_func == NULL) {
    orig_fopen64_func = (orig_fopen64_pt)dlsym(RTLD_NEXT, "fopen64");
  }

  // fprintf(stderr, "there is a fopen64!\n");

  FILE *ret = orig_fopen64_func(__filename, __modes);
  if (ret != NULL)
    setbuf(ret, NULL);

  return ret;
}
