> [!TIP]
> All shell commands shown assume you are cd'd into the `playwright/` directory

### Local setup

Setup playwright project dependencies:

```sh
npm install
# NOTE: do not overwrite existing files
npm init playwright@latest --yes -- . --quiet --browser=chromium
```

If you are using VS Code, it is also recommended that you [install the Playwright extension for VS Code](https://playwright.dev/docs/getting-started-vscode) and open the `playwright/` directory in its own editor session.

### Running tests locally

Before running any tests, you will have to start the backend test-server:

```sh
make -C ../backend test-server
```

Now, in another shell, you can run the end-to-end test suite:

```sh
npx playwright test
```

### Running tests in CI

By default, Playwright assumes the test server is already running. You can disable this behavior and force Playwright to start its own test web server by setting `CI=True` in your shell:

```sh
cd playwright
CI=true npx playwright test
```

This command will cause Playwright to launch the test-server (including rebuilding the database and compiling frontend assets) in docker and then shut it down at the end of the test suite.

## Writing new tests

The easiest way to write tests is with [codegen](https://playwright.dev/docs/codegen), a tool for writing test code by clicking in a browser. You can generate tests against the test-server by running:

```sh
npx playwright codegen localhost:8008
```

ALWAYS READ OVER THE TEST CODE BEFORE COMMITTING. It will not follow project conventions.