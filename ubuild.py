def main(build):
    build.packages.install(".", develop=True)


def test(build):
    main(build)
    build.packages.install("httpretty")
    build.packages.install("mock")
    build.packages.install("pytest")
    build.packages.install("nose")
    code = build.executables.run(
        ["py.test", "tests"] + build.options.args
    )[0]
    if code != 0:
        return code
    return build.executables.run(
        ["py.test", "sprinter"] + build.options.args
    )[0]
