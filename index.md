---
layout: homepage
permalink: /
---

This website archives and collects Intel Product Change Notifications.

- An RSS Feed is available at [/feed.xml](/feed.xml).
- A SQLite export is [published on GitHub](https://github.com/captn3m0/intel-pcn/releases/latest)
- There is an API available that returns each PCN individually.

<table>
	<thead>
		<tr>
			<th>PCN</th>
			<th>Title</th>
			<th>Date</th>
		</tr>
	</thead>
	<tbody>
		{% assign pcns = site.data.pcn | sort:"createddate" | reverse %}
		{% for pcn in pcns %}
		<tr>
			<td><code>{{ pcn.contentid }}</code></td>
			<td><a href="/pcn/{{ pcn.contentid }}/">{{ pcn.systitle | title}}</a></td>
			<td data-order={{pcn.createddate}}>{{ pcn.createddate | divided_by:1000 | date_to_long_string }}</td>
		</tr>
		{% endfor %}
	</tbody>
</table>

Created by [Nemo](https://github.com/captn3m0).