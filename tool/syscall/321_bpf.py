
import os
import textwrap

def generate_bpf_tests():
    output_dir = "./tool/cfiles/321_bpf"
    os.makedirs(output_dir, exist_ok=True)

    tests = {
        "bpf_map_create": textwrap.dedent("""\
            #include <stdio.h>
            #include <stdlib.h>
            #include <unistd.h>
            #include <errno.h>
            #include <linux/bpf.h>
            #include <sys/syscall.h>

            int main(int argc, char **argv)
            {
                union bpf_attr attr = {
                    .map_type    = BPF_MAP_TYPE_HASH,
                    .key_size    = sizeof(int),
                    .value_size  = sizeof(int),
                    .max_entries = 1,
                };

                int fd = syscall(__NR_bpf, BPF_MAP_CREATE, &attr, sizeof(attr));

                if (fd < 0) {
                    if (errno == EPERM) {
                        return EXIT_SUCCESS;
                    }
                    return EXIT_FAILURE;
                }

                close(fd);
                return EXIT_SUCCESS;
            }
        """),

        "bpf_prog_load": textwrap.dedent("""\
            #include <stdio.h>
            #include <stdlib.h>
            #include <unistd.h>
            #include <errno.h>
            #include <linux/bpf.h>
            #include <sys/syscall.h>

            #define BPF_EXIT_INSN() \\
                ((struct bpf_insn) {{ .code = BPF_JMP | BPF_EXIT }})

            int main(int argc, char **argv)
            {
                struct bpf_insn insns[] = {
                    BPF_EXIT_INSN(),
                };

                union bpf_attr attr = {
                    .prog_type = BPF_PROG_TYPE_SOCKET_FILTER,
                    .insn_cnt  = sizeof(insns) / sizeof(struct bpf_insn),
                    .insns     = (unsigned long)insns,
                    .license   = (unsigned long)"GPL",
                };

                int fd = syscall(__NR_bpf, BPF_PROG_LOAD, &attr, sizeof(attr));

                if (fd < 0) {
                    if (errno == EPERM) {
                        return EXIT_SUCCESS;
                    }
                    return EXIT_FAILURE;
                }
                
                close(fd);
                return EXIT_SUCCESS;
            }
        """),

        "bpf_obj_get_info_by_fd": textwrap.dedent("""\
            #include <stdio.h>
            #include <stdlib.h>
            #include <unistd.h>
            #include <errno.h>
            #include <string.h>
            #include <linux/bpf.h>
            #include <sys/syscall.h>

            int main(int argc, char **argv)
            {
                union bpf_attr create_attr = {
                    .map_type    = BPF_MAP_TYPE_HASH,
                    .key_size    = sizeof(int),
                    .value_size  = sizeof(int),
                    .max_entries = 1,
                };

                int map_fd = syscall(__NR_bpf, BPF_MAP_CREATE, &create_attr, sizeof(create_attr));
                if (map_fd < 0) {
                    if (errno == EPERM) {
                        return EXIT_SUCCESS;
                    }
                    return EXIT_FAILURE;
                }

                struct bpf_map_info info = {};
                union bpf_attr info_attr = {
                    .info.bpf_fd = map_fd,
                    .info.info_len = sizeof(info),
                    .info.info = (unsigned long)&info,
                };

                int ret = syscall(__NR_bpf, BPF_OBJ_GET_INFO_BY_FD, &info_attr, sizeof(info_attr));
                
                close(map_fd);

                if (ret != 0) {
                    return EXIT_FAILURE;
                }

                return EXIT_SUCCESS;
            }
        """),

        "bpf_map_operations": textwrap.dedent("""\
            #include <stdio.h>
            #include <stdlib.h>
            #include <unistd.h>
            #include <errno.h>
            #include <linux/bpf.h>
            #include <sys/syscall.h>

            int main(int argc, char **argv)
            {
                union bpf_attr create_attr = {
                    .map_type    = BPF_MAP_TYPE_HASH,
                    .key_size    = sizeof(int),
                    .value_size  = sizeof(long),
                    .max_entries = 10,
                };
                int map_fd = syscall(__NR_bpf, BPF_MAP_CREATE, &create_attr, sizeof(create_attr));
                if (map_fd < 0) {
                    if (errno == EPERM) return EXIT_SUCCESS;
                    return EXIT_FAILURE;
                }

                int key = 1;
                long value = 12345;
                union bpf_attr update_attr = { .map_fd = map_fd, .key = (unsigned long)&key, .value = (unsigned long)&value, .flags = BPF_ANY, };
                if (syscall(__NR_bpf, BPF_MAP_UPDATE_ELEM, &update_attr, sizeof(update_attr)) != 0) {
                    close(map_fd); return EXIT_FAILURE;
                }

                long read_value = 0;
                union bpf_attr lookup_attr = { .map_fd = map_fd, .key = (unsigned long)&key, .value = (unsigned long)&read_value, };
                if (syscall(__NR_bpf, BPF_MAP_LOOKUP_ELEM, &lookup_attr, sizeof(lookup_attr)) != 0) {
                    close(map_fd); return EXIT_FAILURE;
                }

                union bpf_attr delete_attr = { .map_fd = map_fd, .key = (unsigned long)&key, };
                if (syscall(__NR_bpf, BPF_MAP_DELETE_ELEM, &delete_attr, sizeof(delete_attr)) != 0) {
                    close(map_fd); return EXIT_FAILURE;
                }

                close(map_fd);
                return EXIT_SUCCESS;
            }
        """),

        "bpf_map_get_next_key": textwrap.dedent("""\
            #include <stdio.h>
            #include <stdlib.h>
            #include <unistd.h>
            #include <errno.h>
            #include <linux/bpf.h>
            #include <sys/syscall.h>

            int main(int argc, char **argv)
            {
                union bpf_attr create_attr = {
                    .map_type    = BPF_MAP_TYPE_HASH,
                    .key_size    = sizeof(int),
                    .value_size  = sizeof(int),
                    .max_entries = 2,
                };
                int map_fd = syscall(__NR_bpf, BPF_MAP_CREATE, &create_attr, sizeof(create_attr));
                if (map_fd < 0) {
                    if (errno == EPERM) return EXIT_SUCCESS;
                    return EXIT_FAILURE;
                }

                int key1 = 1, value1 = 100;
                union bpf_attr update_attr1 = { .map_fd = map_fd, .key = (unsigned long)&key1, .value = (unsigned long)&value1 };
                syscall(__NR_bpf, BPF_MAP_UPDATE_ELEM, &update_attr1, sizeof(update_attr1));
                
                int next_key = 0;
                union bpf_attr next_key_attr = { .map_fd = map_fd, .key = 0, .next_key = (unsigned long)&next_key, };
                if (syscall(__NR_bpf, BPF_MAP_GET_NEXT_KEY, &next_key_attr, sizeof(next_key_attr)) != 0) {
                    close(map_fd);
                    return EXIT_FAILURE;
                }
                
                close(map_fd);
                return EXIT_SUCCESS;
            }
        """),

        "bpf_map_create_array": textwrap.dedent("""\
            #include <stdio.h>
            #include <stdlib.h>
            #include <unistd.h>
            #include <errno.h>
            #include <linux/bpf.h>
            #include <sys/syscall.h>

            int main(int argc, char **argv)
            {
                union bpf_attr attr = {
                    .map_type    = BPF_MAP_TYPE_ARRAY,
                    .key_size    = sizeof(int),
                    .value_size  = sizeof(long),
                    .max_entries = 128,
                };

                int fd = syscall(__NR_bpf, BPF_MAP_CREATE, &attr, sizeof(attr));

                if (fd < 0) {
                    if (errno == EPERM) {
                        return EXIT_SUCCESS;
                    }
                    return EXIT_FAILURE;
                }

                close(fd);
                return EXIT_SUCCESS;
            }
        """)
    }

    for name, c_code in tests.items():
        filename = os.path.join(output_dir, f"{name}.c")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(c_code)

if __name__ == "__main__":
    generate_bpf_tests()

