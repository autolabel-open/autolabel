#include <linux/ip.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/version.h>
#include <linux/random.h>
#include <net/tcp.h>
#include <net/udp.h>

#include <linux/net.h>
#include <linux/net_namespace.h>
#include <linux/nsproxy.h>
#include <linux/pid.h>

#include "filter.h"

// 定义我们将要使用的Netfilter钩子函数
static struct nf_hook_ops nfho_inputs[CONTAINER_NUMS];
static struct nf_hook_ops nfho_outputs[CONTAINER_NUMS];

static char *src_ports[CONTAINER_NUMS];

struct net *get_net_ns_by_pid(pid_t pid) {
  struct pid *vpid;
  struct task_struct *task;
  struct net *net = NULL;

  vpid = find_get_pid(pid);

  if (!vpid)
    goto out;

  task = pid_task(vpid, PIDTYPE_PID);
  if (!task || !task->nsproxy)
    goto put_pid;

  net = get_net(task->nsproxy->net_ns);

put_pid:
  put_pid(vpid);
out:
  return net;
}

// 实际的钩子函数实现
unsigned int hook_func_input(void *priv, struct sk_buff *skb,
                             const struct nf_hook_state *state) {
  struct iphdr *iph; // ip header struct
  unsigned short dport = 0;
  int i = 0;
  int container_id = (long)priv;

  iph = ip_hdr(skb); // get ip header
  // printk(KERN_INFO "Catched traffic from %pI4 to %pI4\n", &iph->saddr,
  //          &iph->daddr);

  if (iph->protocol != IPPROTO_TCP && iph->protocol != IPPROTO_UDP) {
    return NF_ACCEPT;
  }

  if (iph->protocol == IPPROTO_TCP) {
    struct tcphdr *tcph = tcp_hdr(skb);
    dport = ntohs(tcph->dest);
  } else {
    struct udphdr *udph = udp_hdr(skb);
    dport = ntohs(udph->dest);
  }

  if (src_ports[container_id][dport]) {
    for (i = 0; i < HACK_LEN; ++i) {
      if (iph->saddr == htonl(dst_ips[container_id][i])) {
        iph->frag_off |= htons(0x8000);
        iph->saddr = htonl(key_ips[container_id][i]);
        iph->daddr = htonl(gateway_ips[container_id][i]);
        // printk(KERN_INFO "Matched %d. changed %pI4 -> %pI4:%d\n", i,
        // &iph->saddr, &iph->daddr, dport);

        ip_send_check(iph);
        if (iph->protocol == IPPROTO_TCP) {
          struct tcphdr *tcph = tcp_hdr(skb);
          tcph->check = 0;
          tcph->check = tcp_v4_check(skb->len, iph->saddr, iph->daddr,
                                     csum_partial(tcph, skb->len, 0));
        } else {
          struct udphdr *udph = udp_hdr(skb);
          udph->check = 0;
          udph->check = udp_v4_check(skb->len, iph->saddr, iph->daddr,
                                     csum_partial(udph, skb->len, 0));
        }
#if (LINUX_VERSION_CODE >= KERNEL_VERSION(5, 4, 0))
        if (ip_route_me_harder(state->net, NULL, skb, RTN_UNSPEC) != 0) {
#else
        if (ip_route_me_harder(state->net, skb, RTN_UNSPEC) != 0) {
#endif
          return NF_DROP;
        }
        // printk(KERN_INFO "ACCEPT\n");
        return NF_ACCEPT;
      }
    }
  }

  return NF_ACCEPT; // accept all traffic
}

unsigned int hook_func_output(void *priv, struct sk_buff *skb,
                              const struct nf_hook_state *state) {
  struct iphdr *iph; // ip header struct
  unsigned short sport = 0;
  int i = 0;
  int container_id = (long)priv;

  iph = ip_hdr(skb); // get ip header
  // printk(KERN_INFO "Catched traffic from %pI4 to %pI4\n", &iph->saddr,
  // &iph->daddr);

  if (iph->protocol != IPPROTO_TCP && iph->protocol != IPPROTO_UDP) {
    return NF_ACCEPT;
  }

  // 获取源端口和目标端口
  if (iph->protocol == IPPROTO_TCP) {
    struct tcphdr *tcph = tcp_hdr(skb);
    sport = ntohs(tcph->source);
  } else {
    struct udphdr *udph = udp_hdr(skb);
    sport = ntohs(udph->source);
  }

  for (i = 0; i < HACK_LEN; ++i) {
    if (iph->daddr == htonl(key_ips[container_id][i])) {
      iph->frag_off |= htons(0x8000);
      iph->saddr = htonl(src_ips[container_id][i]);
      iph->daddr = htonl(dst_ips[container_id][i]);
      src_ports[container_id][sport] = 1;

      // printk(KERN_INFO "Matched %d. changed %pI4:%d -> %pI4\n", i,
      // &iph->saddr, sport, &iph->daddr);

      ip_send_check(iph);
      if (iph->protocol == IPPROTO_TCP) {
        struct tcphdr *tcph = tcp_hdr(skb);
        tcph->check = 0;
        tcph->check = tcp_v4_check(skb->len, iph->saddr, iph->daddr,
                                   csum_partial(tcph, skb->len, 0));
      } else {
        struct udphdr *udph = udp_hdr(skb);
        udph->check = 0;
        udph->check = udp_v4_check(skb->len, iph->saddr, iph->daddr,
                                   csum_partial(udph, skb->len, 0));
      }

#if (LINUX_VERSION_CODE >= KERNEL_VERSION(5, 4, 0))
      if (ip_route_me_harder(state->net, NULL, skb, RTN_UNSPEC) != 0) {
#else
      if (ip_route_me_harder(state->net, skb, RTN_UNSPEC) != 0) {
#endif
        return NF_DROP;
      }
      // printk(KERN_INFO "ACCEPT\n");
      return NF_ACCEPT;
    }
  }

  src_ports[container_id][sport] = 0;
  return NF_ACCEPT;
}

// 初始化模块
int init_module() {
  // struct net *cur_net = current->nsproxy->net_ns;
  int i = 0;
  for (i = 0; i < CONTAINER_NUMS; ++i) {
    struct net *cur_net = get_net_ns_by_pid(container_pids[i]);
    struct nf_hook_ops *nfho_input = &nfho_inputs[i];
    struct nf_hook_ops *nfho_output = &nfho_outputs[i];

    printk(KERN_INFO "netns %d: %p\n", i, cur_net);

    src_ports[i] = kmalloc(sizeof(char) * 65536, GFP_KERNEL);
    memset(src_ports[i], 0, CONTAINER_NUMS);

    nfho_input->hook = hook_func_input;
    nfho_input->hooknum = NF_INET_LOCAL_IN;
    nfho_input->pf = PF_INET;
    nfho_input->priority = NF_IP_PRI_FIRST;
    nfho_input->priv = (void *)(long)i;
    nf_register_net_hook(cur_net, nfho_input);

    nfho_output->hook = hook_func_output;
    nfho_output->hooknum = NF_INET_LOCAL_OUT;
    nfho_output->pf = PF_INET;
    nfho_output->priority = NF_IP_PRI_FIRST; // set highest priority
    nfho_output->priv = (void *)(long)i;
    nf_register_net_hook(cur_net, nfho_output); // register hook
  }

  return 0;
}

// 清理模块
void cleanup_module() {
  int i = 0;
  for (i = 0; i < CONTAINER_NUMS; ++i) {
    struct nf_hook_ops *nfho_input = &nfho_inputs[i];
    struct nf_hook_ops *nfho_output = &nfho_outputs[i];
    struct net *cur_net = get_net_ns_by_pid(container_pids[i]);

    printk(KERN_INFO "netns %d: %p\n", i, cur_net);

    kfree(src_ports[i]);
    nf_unregister_net_hook(cur_net, nfho_input);  // unregister hook
    nf_unregister_net_hook(cur_net, nfho_output); // unregister hook
    put_net(cur_net);
  }
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("pyh");
MODULE_DESCRIPTION("Make filter");
MODULE_VERSION("0.01");
