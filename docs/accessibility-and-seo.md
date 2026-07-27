# Accessibility, universal rendering, and SEO

## Why Nuxt is used

Plain client-side Vue can deliver an application, but the workshop needs a public route whose meaningful content and metadata are available in the initial response. Nuxt universal rendering provides server-rendered HTML and then hydrates it into an interactive Vue application.

## Public route contract

```text
/public/projects/[slug]
```

The route:

- fetches public project data during server rendering;
- returns a real `404` for missing/private projects;
- sets page-specific title and description;
- publishes Open Graph metadata;
- uses semantic headings and content;
- remains readable without authenticated client state.

## SSR versus prerendering versus client rendering

- **SSR:** generate HTML on each request or cache/revalidate it; fits changing public project data.
- **Prerendering:** generate HTML at build time; fits fixed home/documentation pages.
- **Client rendering:** browser fetches/renders after JavaScript starts; fits protected dashboard interactions where crawlability is not required.

The reference prerenders `/` and applies short stale-while-revalidate behavior to public project routes. Learners must understand that route rules affect freshness, server load, and failure behavior.

## SEO checklist

- unique descriptive `<title>`;
- useful meta description;
- one clear page-level heading;
- crawlable text in initial HTML;
- canonical URL when custom domains are configured;
- appropriate `robots` behavior for private/auth pages;
- Open Graph/Twitter metadata for shareable pages;
- meaningful `404` status rather than a soft-404 success page;
- sitemap and robots file before real launch;
- stable, readable public URLs;
- performance and mobile usability;
- structured data only when it accurately represents content.

SEO is not guaranteed ranking. It is accurate, accessible, crawlable delivery plus product/content quality.

## Accessibility baseline

- use native buttons, links, labels, lists, headings, and form controls;
- every input has a programmatic label;
- keyboard users can reach and operate all controls;
- visible focus is preserved;
- error messages identify the problem and are not color-only;
- loading and disabled states are understandable;
- heading order communicates structure;
- text contrast and zoom are usable;
- status/priority includes text, not only color;
- reduced motion and responsive layout are respected where animation exists.

## Testing

Manual:

1. complete the critical journey using only keyboard;
2. zoom to 200%;
3. inspect narrow viewport and long text;
4. disable JavaScript and inspect public page content;
5. inspect initial response source and metadata;
6. check focus after errors/navigation.

Automated extensions may add axe-core checks, HTML validation, Lighthouse CI, and page-performance budgets. Automated accessibility checks find only a subset of barriers; manual and assistive-technology review remains necessary.
