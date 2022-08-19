import contextlib
import subprocess


@contextlib.contextmanager
def stashed_changes():
    subprocess.run(("git", "stash"), check=False)

    try:
        yield
    finally:
        subprocess.run(("git", "stash", "pop"), check=False)


@contextlib.contextmanager
def main_branch():
    subprocess.run(("git", "switch", "main"), check=False)

    try:
        yield
    finally:
        subprocess.run(("git", "switch", "-"), check=False)


def main():
    cmds = (
        ("git", "merge", "dev"),
        ("git", "push"),
    )

    with stashed_changes():
        with main_branch():
            for cmd in cmds:
                print(str.join(' ', cmd), flush=True)

                try:
                    subprocess.run(cmd, check=True)
                except subprocess.CalledProcessError:
                    break


if __name__ == '__main__':
    main()
