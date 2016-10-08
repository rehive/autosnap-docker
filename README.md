## Quickstart

- Add a `.env` file that specifies `GOOGLE_APPLICATION_CREDENTIALS`, `PROJECT`, `DISK`, `ZONE` and `INTERVAL_MINUTES`. Have a look at example.env.

- Run `docker-compose up`.

## Deployments

- For remote deployments, add a `PROJECT_NAME` and `HOST_NAME` to the `.env` file.

- Run `fab e deploy` and then `fab e compose:up`

- There is also support for custom env files, e.g. `fab e:staging deploy`
