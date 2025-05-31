#include <linux/file.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/namei.h>
#include <linux/nsproxy.h>
#include <linux/binfmts.h>
#include <linux/pid_namespace.h>
#include <linux/random.h>
#include <linux/syscalls.h>
#include <linux/time.h>
#include <linux/timekeeping.h>
#include <linux/types.h>
#include <linux/uaccess.h>
#include <linux/version.h>

#include "ftrace_helper.h"
#include "write_uuid.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("XXXXX");
MODULE_DESCRIPTION("write syscall hook");
MODULE_VERSION("0.01");

static DEFINE_MUTEX(write_lock);

#if defined(CONFIG_X86_64) && (LINUX_VERSION_CODE >= KERNEL_VERSION(4, 17, 0))
#define PTREGS_SYSCALL_STUBS 1
#endif

#if defined(CONFIG_X86_64) && (LINUX_VERSION_CODE >= KERNEL_VERSION(5, 0, 0))
#define X64_SYSCALL 1
#endif

#if LINUX_VERSION_CODE >= KERNEL_VERSION( 3, 10, 0 )
struct user_arg_ptr {
#ifdef CONFIG_COMPAT
	bool is_compat;
#endif
	union {
		const char __user *const __user *native;
#ifdef CONFIG_COMPAT
		const compat_uptr_t __user *compat;
#endif
	} ptr;
};
#endif


static const char __user *get_user_arg_ptr( struct user_arg_ptr argv, int nr )
{
	const char __user *native;

#ifdef CONFIG_COMPAT
	if ( unlikely( argv.is_compat ) )
	{
		compat_uptr_t compat;

		if ( get_user( compat, argv.ptr.compat + nr ) )
			return(ERR_PTR( -EFAULT ) );

		return(compat_ptr( compat ) );
	}
#endif

	if ( get_user( native, argv.ptr.native + nr ) )
		return(ERR_PTR( -EFAULT ) );

	return(native);
}


static int tmp_count( struct user_arg_ptr argv, int max )
{
	int i = 0;

	if ( argv.ptr.native != NULL )
	{
		for (;; )
		{
			const char __user *p = get_user_arg_ptr( argv, i );

			if ( !p )
				break;

			if ( IS_ERR( p ) )
				return(-EFAULT);

			if ( i >= max )
				return(-E2BIG);
			++i;

			if ( fatal_signal_pending( current ) )
				return(-ERESTARTNOHAND);
			cond_resched();
		}
	}
	return(i);
}


static size_t mnt_ns_id[CONTAINER_NUMS];

struct mnt_namespace *get_mnt_ns_by_pid(pid_t pid) {
  struct pid *vpid;
  struct task_struct *task;
  struct mnt_namespace *mnt_ns = NULL;

  vpid = find_get_pid(pid);

  if (!vpid)
    goto out;

  task = pid_task(vpid, PIDTYPE_PID);
  if (!task || !task->nsproxy)
    goto put_pid;

  mnt_ns = task->nsproxy->mnt_ns;
put_pid:
  put_pid(vpid);
out:
  return mnt_ns;
}


#ifdef PTREGS_SYSCALL_STUBS
static asmlinkage long (*orig_execve)(const struct pt_regs *);

asmlinkage long hook_execve(const struct pt_regs *regs)
{
  const char __user *const __user *argv = (const char __user *const __user *)regs->si;

#else
static asmlinkage long (*orig_execve)(const char __user *filename,
                                      const char __user *const __user *argv,
                                      const char __user *const __user *envp);

asmlinkage long hook_execve(const char __user *filename,
                            const char __user *const __user *argv,
                            const char __user *const __user *envp) {
#endif
  
  int i = 0, len = 0;
  const char __user* native = NULL;
  int tmp_argc = 0;
  char const __user * * new_regs = NULL;
  char const __user * * old_regs = NULL;
  char *kernel_str = NULL;
  long ret;
  int new_reg_len = 0;
  struct user_arg_ptr	argvx	= { .ptr.native = argv };
  tmp_argc = tmp_count( argvx, MAX_ARG_STRINGS );
  if (tmp_argc < 0) return -EFAULT;
  kernel_str = kmalloc(MAX_ARG_STRLEN, GFP_KERNEL);
  new_regs = kmalloc((tmp_argc+1) * sizeof(char __user *), GFP_KERNEL);
  old_regs = kmalloc((tmp_argc+1) * sizeof(char __user *), GFP_KERNEL);
  if (!new_regs || !old_regs || !kernel_str) {
    if (new_regs) kfree(new_regs);
    if (old_regs) kfree(old_regs);
    if (kernel_str) kfree(kernel_str);
    return -ENOMEM;
  }
  for (i = 0; i < tmp_argc; i++) {
    native = get_user_arg_ptr( argvx, i );
    len = strnlen_user( native, MAX_ARG_STRLEN );
    old_regs[i] = native;
    copy_from_user(kernel_str, native, len);
    if (len >= 10 && strncmp(kernel_str, "A#t#k#F#l#", 10) == 0)
      continue; // 如果是A#t#k#F#l#，忽略这个参数
    new_regs[new_reg_len++] = native; // 如果不是A#t#k#F#l#，则这个参数要保留
  }
  for (i = 0; i <= new_reg_len; ++i) {
    if (i != new_reg_len) { // 将新的参数扔到这个位置
      put_user(new_regs[i],
	       (char __user * __user *)(argv) + i);
    } else {
      char __user *tmp_str = NULL;
      put_user(tmp_str, // 最后面加一个NULL
	       (char __user * __user *)(argv) + i);
    }
  }

#ifdef PTREGS_SYSCALL_STUBS
  struct pt_regs new_ret_regs = *regs;
  new_ret_regs.si = (unsigned long)argv;
  ret = orig_execve(&new_ret_regs);
#else
  ret = orig_execve(filename, argv, envp);
#endif

  for (i = 0; i <= tmp_argc; ++i) {
    if (i != tmp_argc) // 还原原有的参数
      put_user(old_regs[i],
	       (char __user * __user *)(argv) + i);
    else { // 最后面加一个NULL
      char __user *tmp_str = NULL;
      put_user(tmp_str,
	       (char __user * __user *)(argv) + i);
    }
  }
  return ret;
}


#ifdef PTREGS_SYSCALL_STUBS
static asmlinkage long (*orig_openat)(const struct pt_regs *);

asmlinkage long hook_openat(const struct pt_regs *regs) {
  const char __user *filename;

  if (regs == NULL) return orig_openat(regs);

  filename = (const char __user *)regs->si;

#else
static asmlinkage long (*orig_openat)(int dfd, const char __user *filename,
                                      int flags, umode_t mode);

asmlinkage long hook_openat(int dfd, const char __user *filename, int flags, umode_t mode) {
#endif

  if (filename == NULL) {
#ifdef PTREGS_SYSCALL_STUBS
    return orig_openat(regs);
#else
    return orig_openat(dfd, filename, flags, mode);
#endif
  }

  char kernel_name[11] = {0};
  long copy_ret = strncpy_from_user(kernel_name, filename, 10);

  if (copy_ret >= 10) {
    if (strncmp(kernel_name, "A#t#k#F#l#", 10) == 0) {
      filename += 10;
    }
  }

  long ret;
#ifdef PTREGS_SYSCALL_STUBS
  struct pt_regs new_regs = *regs;
  new_regs.si = (unsigned long)filename;
  ret = orig_openat(&new_regs);
#else
  ret = orig_openat(dfd, filename, flags, mode);
#endif

  return ret;
  
}


#ifdef PTREGS_SYSCALL_STUBS
static asmlinkage long (*orig_write)(const struct pt_regs *);

asmlinkage long hook_write(const struct pt_regs *regs) {
  int fd;
  char delta = 0;
  void __user *buf;
  size_t count;
  if (regs == NULL)
    return -1;

  fd = regs->di;
  buf = (void __user *)regs->si;
  count = regs->dx;

#else
static asmlinkage long (*orig_write)(int fd, const void __user *buf,
                                     size_t count);

asmlinkage long hook_write(int fd, const void __user *buf, size_t count) {
#endif

  // Check if write is called from the container

  int i, lock_acquired = 0;
  struct file *filep;
  char *pathname, *buffer;
  size_t cur_mnt_ns = (size_t)current->nsproxy->mnt_ns;

  for (i = 0; i < CONTAINER_NUMS; ++i)
    if (mnt_ns_id[i] == cur_mnt_ns)
      break;

  if (i == CONTAINER_NUMS) {
    long ret;
#ifdef PTREGS_SYSCALL_STUBS
    ret = orig_write(regs);
#else
    ret = orig_write(fd, buf, count);
#endif
    return ret;
  }

  // Check if the first 10 bytes of the buffer is "A#t#k#F#l#"

  if (count >= 10) {
    char prefix[10];
    long copy_ret = strncpy_from_user(prefix, (const char __user *)buf, 10);
    if (copy_ret >= 10) {
      if (strncmp(prefix, "A#t#k#F#l#", 10) == 0) {
        buf += 10;
        count -= 10;
        delta = 1;
      }
    }
  }

  // Check if the file is in the applog directory

  filep = fget(fd);

  if (filep) {
    buffer = kmalloc(PATH_MAX, GFP_KERNEL);

    if (buffer) {
      pathname = d_path(&filep->f_path, buffer, PATH_MAX);

      if (strncmp(pathname, applog_path_prefixes[i],
                  strlen(applog_path_prefixes[i])) == 0) {
        struct timespec64 ts;
        ktime_get_real_ts64(&ts);

        struct tm tm;
        time64_to_tm(ts.tv_sec, 0, &tm);

        char timestamp_str[64];
        snprintf(timestamp_str, sizeof(timestamp_str),
                 "%04d-%02d-%02d %02d:%02d:%02d.%09lu %d ", tm.tm_year + 1900,
                 tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec,
                 ts.tv_nsec, task_pid_vnr(current));

        mutex_lock(&write_lock); // 加锁
        lock_acquired = 1;
        kernel_write(filep, timestamp_str, strlen(timestamp_str),
                     &filep->f_pos);
      }

      kfree(buffer);
    }

    fput(filep);
  }

  long ret;
#ifdef PTREGS_SYSCALL_STUBS
  struct pt_regs new_regs = *regs;
  new_regs.si = (unsigned long)buf;
  new_regs.dx = count;
  ret = orig_write(&new_regs);
#else
  ret = orig_write(fd, buf, count);
#endif

  ret = (ret < 0) ? ret : (ret + (delta == 1 ? 10 : 0));

  if (lock_acquired) {
    mutex_unlock(&write_lock); // 如果之前加锁了，现在解锁
  }

  return ret;
}

static struct ftrace_hook hooks[] = {
#ifdef X64_SYSCALL
    HOOK("__x64_sys_write", hook_write, &orig_write),
    HOOK("__x64_sys_openat", hook_openat, &orig_openat),
    HOOK("__x64_sys_execve", hook_execve, &orig_execve),
#else
    HOOK("sys_write", hook_write, &orig_write),
    HOOK("sys_openat", hook_openat, &orig_openat),
    HOOK("sys_execve", hook_execve, &orig_execve),
#endif
};

static int __init rootkit_init(void) {
  int err, i;
  for (i = 0; i < CONTAINER_NUMS; ++i) {
    mnt_ns_id[i] = (size_t)get_mnt_ns_by_pid(container_pids[i]);
  }

  err = fh_install_hooks(hooks, ARRAY_SIZE(hooks));
  if (err)
    return err;

  printk(KERN_INFO "%s: loaded\n", __FILE__);
  return 0;
}

static void __exit rootkit_exit(void) {
  fh_remove_hooks(hooks, ARRAY_SIZE(hooks));
  printk(KERN_INFO "%s: unloaded\n", __FILE__);
}

module_init(rootkit_init);
module_exit(rootkit_exit);
