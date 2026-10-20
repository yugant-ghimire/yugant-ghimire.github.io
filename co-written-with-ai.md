---
layout: page
title: Co-written with AI
permalink: /co-written-with-ai/
---

Research and writing I produced together with AI. I set the questions, direction and checks; the AI did much of the drafting, data gathering and analysis. Sources are cited in each piece.

{% assign ai_posts = site.posts | where: "co_written_with_ai", true %}
<ul class="post-list">
  {%- assign date_format = site.minima.date_format | default: "%b %-d, %Y" -%}
  {%- for post in ai_posts %}
  <li>
    <span class="post-meta">{{ post.date | date: date_format }}</span>
    <h3>
      <a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
    </h3>
  </li>
  {%- endfor %}
</ul>
