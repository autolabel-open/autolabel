/*

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
#include <sys/time.h>
#include <stdlib.h>
#include <pthread.h> // 引入线程库


typedef int (*orig_socket_pt)(int domain, int type, int protocol);
typedef int (*orig_socketpair_pt)(int domain, int type, int protocol, int sv[2]);
typedef int (*orig_accept_pt)(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
typedef int (*orig_accept4_pt)(int sockfd, struct sockaddr *addr, socklen_t *addrlen, int flags);
typedef int (*orig_getsockopt_pt)(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
typedef int (*orig_setsockopt_pt)(int sockfd, int level, int optname, const void *optval, socklen_t optlen);

static orig_socket_pt orig_socket_func = NULL;
static orig_socketpair_pt orig_socketpair_func = NULL;
static orig_accept_pt orig_accept_func = NULL;
static orig_accept4_pt orig_accept4_func = NULL;
static orig_getsockopt_pt orig_getsockopt_func = NULL;
static orig_setsockopt_pt orig_setsockopt_func = NULL;


// 使用 thread-local 存储来保持每个线程的随机种子
static __thread unsigned int rand_seed = 0;


// 线程安全的初始化种子函数
void init_thread_safe_seed() {
  if (rand_seed == 0) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    rand_seed = tv.tv_sec * 1000000 + tv.tv_usec;  // 初始化种子
  }
}


unsigned long long thread_safe_rand() {
  return ((unsigned long long)rand_r(&rand_seed) << 32) | rand_r(&rand_seed);
}


void set_ip_options(int sockfd) {
  if (orig_getsockopt_func == NULL) {
    orig_getsockopt_func = (orig_getsockopt_pt)dlsym(RTLD_NEXT, "getsockopt");
  }
  if (orig_setsockopt_func == NULL) {
    orig_setsockopt_func = (orig_setsockopt_pt)dlsym(RTLD_NEXT, "setsockopt");
  }

  unsigned char pre_ip_options[40];
  unsigned char inserted_ip_options[12];
  // unsigned char new_ip_options[40];
  socklen_t optlen = sizeof(pre_ip_options);
  if (orig_getsockopt_func(sockfd, IPPROTO_IP, IP_OPTIONS, pre_ip_options, &optlen) < 0) {
    perror("Failed to get IP_OPTIONS");
    return;
  }

  if (optlen + sizeof(inserted_ip_options) > sizeof(pre_ip_options)) {
    perror("IP_OPTIONS buffer is too small");
    return;
  }

  unsigned long long tracking_number_1 = thread_safe_rand();
  unsigned long long tracking_number_2 = thread_safe_rand();

  inserted_ip_options[0] = 0xDD;
  inserted_ip_options[1] = 12;
  memcpy(&inserted_ip_options[2], &tracking_number_1, sizeof(tracking_number_1));
  memcpy(&inserted_ip_options[2 + sizeof(tracking_number_1)], &tracking_number_2, sizeof(inserted_ip_options) - 2 - sizeof(tracking_number_1));

  memcpy(&pre_ip_options[optlen], inserted_ip_options, sizeof(inserted_ip_options));

  if (orig_setsockopt_func(sockfd, IPPROTO_IP, IP_OPTIONS, pre_ip_options, optlen + sizeof(inserted_ip_options)) < 0) {
    perror("Failed to set IP_OPTIONS");
    return;
  }
}


int accept4(int sockfd, struct sockaddr *addr, socklen_t *addrlen, int flags) {
  init_thread_safe_seed();

  if (orig_accept4_func == NULL) {
    orig_accept4_func = (orig_accept4_pt)dlsym(RTLD_NEXT, "accept4");
  }

  int new_sockfd = orig_accept4_func(sockfd, addr, addrlen, flags);
  if (new_sockfd >= 0) {
    set_ip_options(new_sockfd);
  }

  return new_sockfd;
}


int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen) {
  init_thread_safe_seed();

  if (orig_accept_func == NULL) {
    orig_accept_func = (orig_accept_pt)dlsym(RTLD_NEXT, "accept");
  }

  int new_sockfd = orig_accept_func(sockfd, addr, addrlen);
  if (new_sockfd >= 0) {
    set_ip_options(new_sockfd);
  }

  return new_sockfd;
}

int socket(int domain, int type, int protocol) {
  init_thread_safe_seed();

  if (orig_socket_func == NULL) {
    orig_socket_func = (orig_socket_pt)dlsym(RTLD_NEXT, "socket");
  }

  int sockfd = orig_socket_func(domain, type, protocol);
  if (sockfd >= 0) {
    set_ip_options(sockfd);
  }

  return sockfd;
}


int socketpair(int domain, int type, int protocol, int sv[2]) {
  init_thread_safe_seed();

  if (orig_socketpair_func == NULL) {
    orig_socketpair_func = (orig_socketpair_pt)dlsym(RTLD_NEXT, "socketpair");
  }

  int ret = orig_socketpair_func(domain, type, protocol, sv);
  if (ret == 0) {
    set_ip_options(sv[0]);
    set_ip_options(sv[1]);
  }

  return ret;
}

/*
int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen) {
  if (orig_setsockopt_func == NULL) {
    orig_setsockopt_func = (orig_setsockopt_pt)dlsym(RTLD_NEXT, "setsockopt");
  }

  int ret = orig_setsockopt_func(sockfd, level, optname, optval, optlen);
  if (ret == 0) {
    set_ip_options(sockfd);
  }

  return ret;
}
*/
