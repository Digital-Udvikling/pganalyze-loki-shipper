# pganalyze-loki-shipper

Ships logs from loki to pganalyze, specifically for use with [scaleway's](https://www.scaleway.com/en/) managed 
[PostgreSQL](https://www.scaleway.com/en/database/).

## Usage

This application can be deployed as a docker image, and ships logs to the [pganalyze collector](https://pganalyze.com/docs/collector)
via their syslog endpoint, which should be set up by setting the `LOG_SYSLOG_SERVER` environment variable, see more in the [collector's documentation](https://pganalyze.com/docs/collector/settings#self-managed-servers).

### Environment variables

- `LOKI_HOST` - The host of the loki instance, for scaleway this is `logs.cockpit.fr-par.scw.cloud` depending on the region
- `LOKI_TOKEN` - The token to authenticate with loki, for scaleway it should be a cockpit token with the `logs:read` permission
- `LOKI_QUERY` - The query to run against loki, for example `{resource_id="xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx"} |= \`\` `
- `PGANALYZE_SYSLOG` - The syslog endpoint of the pganalyze collector, setup with the `LOG_SYSLOG_SERVER` enviroment variable, for example `1.2.3.4:10000`. If this variable is not set, the logs will be printed to stdout.

### Example

```bash
docker run -e LOKI_HOST=logs.cockpit.fr-par.scw.cloud -e LOKI_X_TOKEN=abcd -e LOKI_QUERY="{resource_id=\"xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx\"} |= ``" -e PGANALYZE_SYSLOG=1.2.3.4:10000 pganalyze-loki-shipper
```