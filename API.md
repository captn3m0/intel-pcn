---
layout: default
title: API Specification
permalink: /api
---

Note: The API does not have any rate-limits or restrictions.

## `/pcn/{ID}.json`

```json
{
	"title": "string",
	"id": "string(int)",
	"created_at": "ISO-8601 datetime",
	"modified_at": "ISO-8601 datetime",
	"description": "string",
	"download_url": "string, direct PDF URL (typically docs.altera.com after Intel's 2025 Altera divestiture; falls back to original_url for documents not yet resolved or gated behind a loginwall)",
	"original_url": "string, the original cdrdv2.intel.com URL as published by Intel",
	"html_url": "string, link to intel.com HTML PCN page",
	"url": "string, link to simpler html pcn page hosted here",
	"category": "string, Content type",
	"self": "string, link to this JSON API URL"
}
```

## `/feed.json`

JSONFeed specification can be found [here](https://jsonfeed.org/version/1).
Feed includes latest 100 PCNs. Each PCN includes the following fields:

1. `url` : PCN HTML page hosted here
2. `external_url`: PCN HTML page hosted at intel.com
3. `attachments[].url`: direct PDF URL (resolved — typically on docs.altera.com)
4. `_original_url`: the original cdrdv2.intel.com URL as published by Intel
5. `api_url`: API URL for the PCN details, as above
6. `id`: PCN ID
7. `title`: PCN Title
8. `date_published` / `date_modified`

## `/feed.xml`

ATOM Format Feed. Link points to the intel.pcn.captnemo.in URL.