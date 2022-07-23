import os


def main(build):
    build.packages.install(".", develop=True)


def test(build):
    main(build)
    build.packages.install("httpretty")
    build.packages.install("mock")
    build.packages.install("pytest")
    build.packages.install("nose")
    build.executables.run(["py.test", "sprinter", "tests"] + build.options.args)
