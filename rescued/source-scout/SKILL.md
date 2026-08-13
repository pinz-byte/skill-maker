---
name: source-scout
description: "Discover, validate, and configure new vehicle listing sources for the AVT Extractor pipeline. Use this skill whenever someone asks to 'find new sources', 'discover data sources', 'add new scrapers', 'expand the extractor', 'find car listing sites', 'scout sources', 'where else can we scrape', or any request about finding new websites or platforms that publish used vehicle listings. Also triggers on 'more comparables data', 'improve data coverage', 'new markets', or 'add a country'. Default market: Peru. Works for any LATAM market."
---

# Source Scout — Vehicle Listing Source Discovery & Configuration

You are an autonomous agent that discovers new scrapeable vehicle listing sources, validates their data quality, generates ready-to-use scraper configurations, and test-scrapes a sample to prove extraction works.

## When to use this skill

- User wants to find new data sources for the AVT comparables engine
- User wants to expand geographic coverage (new LATAM markets)
- User wants to validate whether a specific site is scrapeable
- User wants scraper configs generated for known sites
- The comparables collection needs more data volume or diversity

## Architecture context

The AVT system uses a Firestore `comparables` collection keyed by `{BRAND}_{MODEL}_{YEAR}`. Data flows in via:
- **Extractor pipeline**: Pub/Sub → `onExtractorData` Cloud Function (neoauto, vmc)
- **Retailer scraper**: `scrapeRetailers` scheduled Cloud Function (daily 4am UTC)
- Each source writes to `scrape_runs` collection for monitoring

Comparable doc schema:
```
{
  avgPrice: number (USD),
  minPrice: number,
  maxPrice: number,
  count: number,
  sources: string[],
  updatedAt: Timestamp
}
```

## Workflow

### Phase 1 — Discovery

Search the web for vehicle listing platforms in the target market. For each market, look for:

1. **Dealer inventory sites** — Concesionarios with online inventory (highest signal, cleanest data)
2. **Certified pre-owned platforms** — Dealer-backed platforms with inspected vehicles
3. **Marketplace aggregators** — Sites that aggregate listings from multiple sources
4. **Classifieds** — Peer-to-peer listing platforms
5. **Meta-aggregators** — Sites like Trovit that aggregate from other aggregators

Search queries to use (adapt per country):
- `"autos usados" {country} sitio web inventario precio`
- `concesionarios {country} autos seminuevos online`
- `compra venta vehiculos usados {country} plataforma`
- `site:*.{tld} autos usados inventario` (where tld = pe, co, cl, ec, mx)
- `{known_brand} seminuevos {country}` (Toyota, Hyundai, Kia — popular brands reveal dealer sites)

For each candidate source, capture:
- **Name** and **URL**
- **Type**: dealer / certified / aggregator / classifieds / meta
- **Estimated volume**: rough listing count
- **Data fields visible**: which of (brand, model, year, price, km, fuel, transmission, color, location) are shown
- **Currency**: USD, PEN, COP, CLP, etc.
- **URL pattern** for listing pages and detail pages

### Phase 2 — Validation

For each discovered source, validate scrapeability:

1. **Fetch the listing page** via WebFetch or browser tools
2. **Check for anti-bot measures**: Cloudflare, captchas, JS-only rendering
3. **Identify data structure**: Is it server-rendered HTML? JSON API? SPA with XHR calls?
4. **Map the DOM**: Find CSS selectors or API endpoints for vehicle data fields
5. **Rate the source** on a 1-5 scale:
   - 5: Clean HTML, all fields present, no anti-bot, pagination works
   - 4: Most fields present, minor parsing needed
   - 3: Requires JS rendering or API reverse-engineering
   - 2: Partial data, heavy anti-bot, fragile
   - 1: Not scrapeable without authentication or browser automation

Only proceed to Phase 3 for sources rated 3+.

### Phase 3 — Scraper Configuration

For each validated source, generate a scraper config object:

```js
{
  id: "source_id",           // lowercase, underscores
  name: "Human Name",
  url: "https://...",         // listing page URL
  type: "dealer|aggregator|classifieds|meta",
  country: "PE",
  currency: "USD",           // or "PEN", "COP", etc.
  penToUsd: 0.27,            // conversion rate if needed
  pagination: {
    type: "url_param|next_link|infinite_scroll|none",
    param: "page",            // if url_param
    maxPages: 10,
  },
  selectors: {
    listingCard: "css selector for each vehicle card",
    brand: "css selector or extraction logic",
    model: "css selector",
    year: "css selector or regex",
    price: "css selector",
    km: "css selector",
    fuel: "css selector (if available)",
    transmission: "css selector (if available)",
    detailUrl: "css selector for link to detail page",
  },
  // OR if it's an API:
  api: {
    endpoint: "https://...",
    method: "GET",
    params: { ... },
    responseMapping: {
      listings: "data.results",
      brand: "item.marca",
      model: "item.modelo",
      // ...
    }
  },
  rateLimit: {
    requestsPerMinute: 10,
    delayMs: 1000,
  },
  notes: "Any quirks, auth requirements, or parsing caveats",
}
```

### Phase 4 — Test Scrape

For each configured source, perform a live test scrape:

1. Fetch the listing page
2. Parse using the configured selectors/API mapping
3. Extract 3-5 sample listings
4. Validate: do the extracted fields make sense? (price in reasonable range, year is 4 digits, km is numeric)
5. Show results in a table:

```
| Brand | Model | Year | Price (USD) | Km | Source |
|-------|-------|------|-------------|-----|--------|
| Toyota | Corolla | 2020 | $15,500 | 45,000 | autosell |
```

6. Flag any extraction issues (missing fields, garbled text, wrong currency)

### Phase 5 — Output

Deliver a structured report:

1. **Source Registry** — All discovered sources with ratings and metadata
2. **Scraper Configs** — Ready-to-paste config objects for the `scrapeRetailers` Cloud Function
3. **Test Results** — Sample data extracted from each source with quality assessment
4. **Recommendations** — Priority order for implementation, estimated data volume impact

Save the source registry and configs to a JSON file for the user to review and feed into the Cloud Function.

## Market-specific notes

### Peru (PE)
- Primary currency: PEN (Soles). Most sites show USD for used cars.
- Key markets: Lima (90%+ of listings), Arequipa, Cusco
- Active sources: neoauto.com (already integrated), mercadolibre.com.pe (deprecated — API locked)
- Conversion: ~3.7 PEN/USD

### Colombia (CO)
- Currency: COP. 1 USD ≈ 4,200 COP
- Key platforms: tucarro.com, fincaraiz.com.co, carroya.com
- TLD: .com.co

### Chile (CL)
- Currency: CLP. 1 USD ≈ 950 CLP
- Key platforms: chileautos.cl, yapo.cl, automotora.cl
- TLD: .cl

### Ecuador (EC)
- Currency: USD (dollarized economy — no conversion needed)
- Key platforms: patiodeautos.com, olx.com.ec
- TLD: .com.ec

### México (MX)
- Currency: MXN. 1 USD ≈ 17 MXN
- Key platforms: seminuevos.com, autocosmos.com.mx, kavak.com
- TLD: .com.mx

## Error handling

- If a source returns 403/429, note it as "rate-limited or auth-required" and move on
- If HTML structure can't be parsed, try checking for a hidden JSON API (look for XHR calls in network tab)
- If a site is fully JS-rendered (React/Vue SPA), check if there's a `__NEXT_DATA__` or `window.__INITIAL_STATE__` JSON blob in the page source
- Never spend more than 5 minutes on a single source that's proving difficult — flag it and move on
