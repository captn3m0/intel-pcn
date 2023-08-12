---
layout: homepage
permalink: /
---

This website archives and collects Intel Product Change Notifications.

- An RSS Feed is available at [/feed.xml](/feed.xml).
- A complete CSV export is [published on GitHub](https://github.com/captn3m0/intel-pcn/blob/main/_data/pcn.csv). You can also check it at <https://flatgithub.com/captn3m0/intel-pcn> as well.

<table>
	<thead>
		<tr>
			<th>PCN</th>
			<th>Title</th>
			<th>Date</th>
		</tr>
	</thead>
	<tbody>
		{% assign pcns = site.data.pcn | sort:"date" | reverse %}
		{% for pcn in pcns %}
		<tr>
			<td><code>{{ pcn.id }}</code></td>
			<td><a href="/pcn/{{ pcn.id }}/">{{ pcn.title |replace: '¬',' '}}</a></td>
			<td>{{ pcn.date | date_to_long_string }}</td>
		</tr>
		{% endfor %}
	</tbody>
</table>

Created by [Nemo](https://github.com/captn3m0).