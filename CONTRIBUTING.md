### Running sandbox.sh locally
From the root sprinter folder run `scripts/sandbox.sh`
    - sprinter files will be copied from the local folder and not downloaded

### Referencing a local copy of Uranium
From the root sprinter folder run `URANIUM_PATH=../uranium/uranium/scripts/uranium_standalone ./scripts/sandbox.sh`

### Referencing an alternate github account for Uranium
From the root sprinter folder run `URANIUM_REPO=MyGithubAccount ./scripts/sandbox.sh`
    - will load from `https://raw.githubusercontent.com/MyGithubAccount/uranium/master/uranium/scripts/uranium_standalone`

### Referencing an alternate remote branch Uranium
From the root sprinter folder run `URANIUM_BRANCH=develop URANIUM_REPO=MyGithubAccount ./scripts/sandbox.sh`
    - will load from `https://raw.githubusercontent.com/MyGithubAccount/uranium/develop/uranium/scripts/uranium_standalone`

## Running unit tests
To run all tests
`./uranium test`
If you have environment errors
`source bin/activate && ./uranium test`

To run a single test
  `nosetests -vs [path to test]`
  example:
  `nosetests -vs sprinter.formula.tests.test_git`
  or
  `nosetests -vs sprinter.formula.tests.test_git:TestGitFormula.test_simple_example`
