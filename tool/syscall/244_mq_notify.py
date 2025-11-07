
import os

def generate_mq_notify_tests():
    output_dir = "./tool/cfiles/244_mq_notify"
    os.makedirs(output_dir, exist_ok=True)

    sigev_notify_types = {
        "SIGEV_NONE": {
            "setup": "sev.sigev_notify = SIGEV_NONE;",
            "handler": ""
        },
        "SIGEV_SIGNAL": {
            "setup": "sev.sigev_notify = SIGEV_SIGNAL; sev.sigev_signo = SIGUSR1;",
            "handler": ""
        },
        "SIGEV_THREAD": {
            "setup": """sev.sigev_notify = SIGEV_THREAD;
    sev.sigev_notify_function = thread_handler;
    sev.sigev_notify_attributes = NULL;
    sev.sigev_value.sival_ptr = NULL;""",
            "handler": """
void thread_handler(union sigval sv) {
}
"""
        }
    }

    for notify_name, notify_config in sigev_notify_types.items():
        c_code = f"""#include <fcntl.h>
#include <sys/stat.h>
#include <mqueue.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <signal.h>
#include <string.h>

#ifndef SYS_mq_open
#define SYS_mq_open 240
#endif
#ifndef SYS_mq_notify
#define SYS_mq_notify 244
#endif
#ifndef SYS_mq_unlink
#define SYS_mq_unlink 241
#endif

{notify_config["handler"]}
int main() {{
    const char *mq_name = "/test_mq_{notify_name.lower()}";
    mqd_t mqd;
    struct sigevent sev;

    mq_unlink(mq_name);

    mqd = mq_open(mq_name, O_CREAT | O_RDONLY, 0644, NULL);
    if (mqd == (mqd_t)-1) {{
        return 1;
    }}

    memset(&sev, 0, sizeof(struct sigevent));
    {notify_config["setup"]}

    if (syscall(SYS_mq_notify, mqd, &sev) == -1) {{
        close(mqd);
        mq_unlink(mq_name);
        return 1;
    }}

    close(mqd);
    mq_unlink(mq_name);
    return 0;
}}
"""
        filename = os.path.join(output_dir, f"mq_notify_{notify_name.lower()}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_mq_notify_tests()
