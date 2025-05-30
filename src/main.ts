import { PlaywrightCrawler } from "crawlee";
import { router } from "./routes.js";

const MAX_REQUESTS_PER_CRAWL = 1000;
const REQUEST_HANDLER_TIMEOUT_SECS = 1200;
const LOG_LEVEL = "info";

const startUrls = [
  "https://www.yaga-burundi.com/kabu-16/",
  "https://www.yaga-burundi.com/yagadecodeur/",
  "https://www.yaga-burundi.com/analyse/",
  "https://www.yaga-burundi.com/carnet-de-voyage/",
  "https://www.yaga-burundi.com/culture/",
  "https://www.yaga-burundi.com/dossiers-yaga/",
  "https://www.yaga-burundi.com/economie/",
  "https://www.yaga-burundi.com/editorial/",
  "https://www.yaga-burundi.com/education/",
  "https://www.yaga-burundi.com/justice/",
  "https://www.yaga-burundi.com/methode-yaga/",
  "https://www.yaga-burundi.com/multimedias/",
  "https://www.yaga-burundi.com/nouvelles/",
  "https://www.yaga-burundi.com/opinion/",
  "https://www.yaga-burundi.com/politique/",
  "https://www.yaga-burundi.com/reactions/",
  "https://www.yaga-burundi.com/revue-de-la-presse/",
  "https://www.yaga-burundi.com/sante/",
  "https://www.yaga-burundi.com/securite/",
  "https://www.yaga-burundi.com/societe/",
  "https://www.yaga-burundi.com/special-10-ans-de-yaga/",
  "https://www.yaga-burundi.com/sport/",
  "https://www.yaga-burundi.com/synergie-des-medias/",
  "https://www.yaga-burundi.com/une-journee-nuit-avec/",
  "https://www.yaga-burundi.com/une-lettre-a/",
  "https://www.yaga-burundi.com/yaga-urukundo/",
  "https://www.yaga-burundi.com/yaga-here/",
];

process.env.CRAWLEE_LOG_LEVEL = LOG_LEVEL;

const crawler = new PlaywrightCrawler({
  requestHandler: router,
  maxRequestsPerCrawl: MAX_REQUESTS_PER_CRAWL,
  requestHandlerTimeoutSecs: REQUEST_HANDLER_TIMEOUT_SECS,
});

await crawler.run(startUrls);
