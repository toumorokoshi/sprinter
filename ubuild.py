def main(build):
    build.packages.install(".", develop=True)


def test(build):
    main(build)
    build.packages.install("httpretty")
    build.packages.install("mock")
    build.packages.install("pytest")
    build.packages.install("nose")
    return build.executables.run(
        ["py.test", "sprinter"] + build.options.args
    )[0]
