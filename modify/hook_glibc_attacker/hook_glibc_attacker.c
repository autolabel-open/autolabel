#define _GNU_SOURCE
#include <arpa/inet.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

#include "ip_list.h"

typedef int (*orig_connect_pt)(int sockfd, const struct sockaddr *addr,
                               socklen_t addrlen);

typedef ssize_t (*orig_sendto_pt)(int sockfd, const void *buf, size_t len,
                                  int flags, const struct sockaddr *dest_addr,
                                  socklen_t addrlen);

static orig_connect_pt orig_connect_func = NULL;
static orig_sendto_pt orig_sendto_func = NULL;

int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen) {
  if (orig_connect_func == NULL) {
    orig_connect_func = (orig_connect_pt)dlsym(RTLD_NEXT, "connect");
  }

  // fprintf(stderr, "connect to %s\n", inet_ntoa(((struct sockaddr_in *)addr)->sin_addr));

  int i = 0;
  struct sockaddr_in modified_addr;

  if (addr->sa_family == AF_INET) {
    memcpy(&modified_addr, addr, sizeof(struct sockaddr_in));
    for (i = 0; i < sizeof(ip_list) / sizeof(ip_list[0]); i++) {
      if (modified_addr.sin_addr.s_addr == inet_addr(ip_list[i][0])) {
        // fprintf(stderr, "modified: connect to %s\n", ip_list[i][1]);
        modified_addr.sin_addr.s_addr = inet_addr(ip_list[i][1]);
        break;
      }
    }
    return orig_connect_func(sockfd, (const struct sockaddr *)&modified_addr,
                             addrlen);
  }
  return orig_connect_func(sockfd, addr, addrlen);
}

ssize_t sendto(int sockfd, const void *buf, size_t len, int flags,
               const struct sockaddr *dest_addr, socklen_t addrlen) {
  if (orig_sendto_func == NULL) {
    orig_sendto_func = (orig_sendto_pt)dlsym(RTLD_NEXT, "sendto");
  }

  // fprintf(stderr, "sendto to %s\n", inet_ntoa(((struct sockaddr_in *)dest_addr)->sin_addr));

  int i = 0;
  struct sockaddr_in modified_addr;
  
  if (dest_addr->sa_family == AF_INET) {
    memcpy(&modified_addr, dest_addr, sizeof(struct sockaddr_in));
    for (i = 0; i < sizeof(ip_list) / sizeof(ip_list[0]); i++) {
      if (modified_addr.sin_addr.s_addr == inet_addr(ip_list[i][0])) {
        // fprintf(stderr, "modified: sendto to %s\n", ip_list[i][1]);
        modified_addr.sin_addr.s_addr = inet_addr(ip_list[i][1]);
        break;
      }
    }
    return orig_sendto_func(sockfd, buf, len, flags,
                            (const struct sockaddr *)&modified_addr, addrlen);
  }
  return orig_sendto_func(sockfd, buf, len, flags, dest_addr, addrlen);
}
