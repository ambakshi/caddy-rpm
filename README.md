### caddy-rpm

Originally taken from https://github.com/carlwgeorge/caddy-rpm , but it seems
the repo has disappeared

```sh
    docker build -t caddy-rpm .
    docker run --rm $(pwd)/output:/output caddy-rpm
```
