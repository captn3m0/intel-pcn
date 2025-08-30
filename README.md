---
layout: homepage
permalink: /
---

# Intel Product Change Notifications

This website archives
[Intel Product Change Notifications](https://www.intel.com/content/www/us/en/collections/content-type/pcns.html)
and makes them available over an API as well to search engines for better indexing.

- Automate daily commits using GitHub Actions.
- An RSS Feed (ATOM format) is available at [/feed.xml](/feed.xml).
- An JSON Feed is available at [/feed.json](/feed.json).
- A SQLite export is [published on GitHub](https://github.com/captn3m0/intel-pcn/releases/latest)
- There is an API available that returns each PCN individually. See [Sample](/api/862098.json)

## API Specification

Note: The API does not have any rate-limits or restrictions.

### `/pcn/{ID}.json`

```json
{
	"title": "string",
	"id": "string(int)",
	"created_at": "ISO-8601 datetime",
	"modified_at": "ISO-8601 datetime",
	"description": "string",
	"download_url": "string, PDF URL to upstream",
	"html_url": "string, link to intel.com HTML PCN page",
	"url": "string, link to simpler html pcn page hosted here",
	"category": "string, Content type",
	"self": "string, link to this JSON API URL"
}
```

### `/feed.json`

JSONFeed specification can be found [here](https://jsonfeed.org/version/1).
Feed includes latest 100 PCNs. Each PCN includes the following fields:

1. `url` : PCN HTML page hosted here
2. `external_url`: PCN HTML page hosted at intel.com
3. `attachment`: PDF URL, hosted at intel.com
4. `api_url`: API URL for the PCN details, as above
5. `id`: PCN ID
5. `title`: PCN Title
6. `date_published` / `date_modified`

### `/feed.xml`

ATOM Format Feed. Link points to the intel.pcn.captnemo.in URL.

## LICENSE

Licensed under MIT. See `LICENSE` file for more details.