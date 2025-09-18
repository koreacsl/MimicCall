
import os

def generate_signalfd_tests():
    output_dir = "./tool/cfiles/282_signalfd"
    os.makedirs(output_dir, exist_ok=True)

    c_code = r"""#include <signal.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/signalfd.h>
#include <errno.h>
#include <stdio.h>

#ifndef SYS_signalfd
#define SYS_signalfd 282
#endif
#ifndef SYS_rt_sigprocmask
#define SYS_rt_sigprocmask 14
#endif
#ifndef SYS_kill
#define SYS_kill 62
#endif

/* 커널이 기대하는 시그널셋 크기(64개 신호 = 8바이트) */
#define KERNEL_SIGSET_BYTES 8

int main(void) {
    sigset_t mask;
    int sfd;
    struct signalfd_siginfo fdsi;

    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);

    /* 시스템콜 직접 호출: 길이는 KERNEL_SIGSET_BYTES로 고정 */
    if (syscall(SYS_rt_sigprocmask, SIG_BLOCK, &mask, NULL, KERNEL_SIGSET_BYTES) == -1) {
        perror("rt_sigprocmask");
        return 1;
    }

    /* signalfd 시스템콜도 동일하게 3번째 인자에 커널 크기 사용 */
    sfd = (int)syscall(SYS_signalfd, -1, &mask, KERNEL_SIGSET_BYTES);
    if (sfd == -1) {
        perror("signalfd");
        return 1;
    }

    /* 신호 보내기 */
    if (syscall(SYS_kill, getpid(), SIGUSR1) == -1) {
        perror("kill");
        close(sfd);
        return 1;
    }

    /* signalfd에서 신호 읽기 */
    ssize_t n = read(sfd, &fdsi, sizeof(fdsi));
    if (n != (ssize_t)sizeof(fdsi)) {
        perror("read(signalfd)");
        close(sfd);
        return 1;
    }

    close(sfd);
    return 0;
}
"""
    filename = os.path.join(output_dir, "signalfd_0.c")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(c_code)

if __name__ == "__main__":
    generate_signalfd_tests()
