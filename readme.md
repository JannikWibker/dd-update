# dd-update

dd-update is a replacement for ddclient which (at least for me) does not work reliably / at all. dd-update takes a similarly structured config file as ddclient does but instead of using `.ini` it uses yaml. Many properties are intentionally the same between ddclient and dd-update. At the moment the only protocol supported by dd-update is cloudflare (v4) but adding support is rather trivial.

dd-update relies on cronjobs to execute as it does not do scheduling on it's own (meaning that it does not have to deal with the same issues that ddclinet faces). Where ddclient would often not run at all cronjobs should do the job just fine.

### Configuration

The config file format looks something like this:

```yml
options:
  use: web
  web: ifconfig.me/ip
  cache: true
  verbose: true

domain.name:
  protocol: cloudflare
  server: api.cloudflare.com/client/v4
  ssl: true
  login: email/username
  password: password/token
  zone: domain.name
```

dd-update requires a global options object which describes how to retrieve the current public ip and wether or not to cache it. ddclient does this independently for each domain but as one installation will probably have multiple public ip addresses to choose from which need to be assigned to specific domains this can be done globally for all domains.

### Command line flags

Almost all of these flags are also available as configuration parameters in the `options` object (config, help and version are excluded as they do not make sense to be included in a config file and no_cache is negated to cache)

The following command line flags can be used:
- `--verbose` (`-v`): Log more stuff (debugging purposes)
- `--domain` (`-d`): Specify which domain to update (debugging purposes; by default everything is updated if outdated)
- `--force` (`-f`): Force update even if cache is fresh (debugging purposes)
- `--no_cache`: Do not save to cache (this option still uses the cache; use `--force` if needed)
- `--silent` (`-s`): Do not log anything
- `--config` (`-c`): Specify a file path where the config file can be found

- `--version`: Show the current version
- `--help` (`-h`): Show a help page

### Running with cronjobs

The following crontab configuration

```
*/30 * * * * python path/to/dd-update.py --config /etc/dd-update.yml --verbose 
```

This site can be used to quickly look up crontab configuration: https://crontab.guru

### Cloudflare protocol & setup

The cloudflare API needs to be supplied with an authorization token in order to update dns records. That token can be optained from the cloudflare dashboard.

Either a custom token can be generated with custom permissions or the **Global API Key** can be used which has **ACCESS TO EVERYTHING** (this is the key that is used by the dashboard itself which ofcourse has full permissions). It is advised to generate a token just for dd-update and use that instead of the global api key.

To generate such a token go to your domain in the dashboard, scroll down a bit and click on

> "Get your API key"

After that go to "API Tokens" and click "Create Token"

Now the exact permissions depend on your config file, you can either include the so called "zone id" by yourself or add the permission to retrieve this id automatically. As it requires additional api calls it is better to just include it manually via `zone_id: <zone_id>` under the domain configuration.

The following permission is always required:

> `Zone` -> `DNS` -> `Edit`

Additionally if retrieving the zone_id should be done by dd-update

> `Zone` -> `Zone` -> `Read`

is also required. Create the token and **copy it** as it is only shown once. Add it to the domain under the property `password`.

If you really want to cut down on requests made each time the ip changes you can also observe dd-update's output using `--verbose` and copy the so called `record_id` to the config file, this will reduce the api calls made for each change from 2 (3 without zone_id) to only 1.

> At the moment these values cannot be cached. This will probably work in the future.

A domain config with all this could look like this:

```yml
domain.name:
  protocol: cloudflare
  server: api.cloudflare.com/client/v4
  ssl: true
  login: email/username
  password: password
  zone: domain.name
  zone_id: 023e105f4ecef8ad9ca31a8372d0c353
  record_id: 372e67954025e0ba6aaa6d586b9e0b59
```

As you use your API Token for authentication and authorization the `login`-field is not required.