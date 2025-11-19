Setup playwright project dependencies:

```sh
npm install
```

Install playwright and the chromium browser to your local machine with:

```sh
npm init playwright@latest --yes -- . --quiet --browser=chromium
```

Run the whole test suite, including a full test backend with static frontend assets, with:

```sh
npx playwright test
```
