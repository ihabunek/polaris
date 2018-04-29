import sys
import subprocess


def main(paths):
    for path in paths:
        cmd = [
            "ebook-convert",
            path,
            path.replace(".html", "") + ".mobi",
            "--output-profile", "kindle",
            "--chapter", "//*[(name()='h1' or name()='h2' or name()='h3' or name()='h4')]",
            "--level1-toc", "//h:h2",
            "--level2-toc", "//h:h3",
            "--level3-toc", "//h:h4",
        ]

        subprocess.run(cmd)


if __name__ == '__main__':
    main(sys.argv[1:])
