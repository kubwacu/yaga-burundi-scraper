import { createPlaywrightRouter, log } from "crawlee";
import * as fs from "fs";
import * as path from "path";
import { Page } from "playwright";
import { ArticleMetadata } from "./types/article.js";

export const router = createPlaywrightRouter();

const saveResults = async (page: Page, allArticles: ArticleMetadata[]) => {
  const outputPath = getOutputPath(page);
  fs.writeFileSync(outputPath, JSON.stringify(allArticles, null, 2));
  log.info(`Saved ${allArticles.length} articles to ${outputPath}`);
};

const getOutputPath = (page: Page) => {
  const currentUrl = page.url();
  let fileName = currentUrl.replace("https://www.yaga-burundi.com", "");
  fileName = fileName.replace(/\/$/, "");
  return path.join("storage", `${fileName}.json`);
};

const getArticlesMetadata = async (page: Page): Promise<ArticleMetadata[]> => {
  const articles = await page.$$("article.type-post");
  const articlesData = await Promise.all(
    articles.map(async (article) => {
      try {
        const header = await article.$("header.entry-header");

        const category = await header?.$("span.subtitle");
        const title = await header?.$("h2.entry-title");
        const url = await title?.$("a");
        const urlValue =
          "https://www.yaga-burundi.com" + (await url?.getAttribute("href")) ||
          null;
        const author = await header?.$(".author.vcard");
        const postedAt = await header?.$("span.posted-on time");

        const postedAtValue = await postedAt?.getAttribute("datetime");
        const authorValue = await author?.textContent();
        const titleValue = await title?.textContent();
        const categoryValue = await category?.textContent();

        if (postedAtValue && authorValue && titleValue && urlValue && categoryValue) {
          return {
            postedAt: postedAtValue,
            author: authorValue,
            title: titleValue,
            url: urlValue,
            category: categoryValue,
          };
        }
        return null;
      } catch (error) {
        log.debug(
          `Error processing article: ${
            error instanceof Error ? error.message : String(error)
          }`
        );
        return null;
      }
    })
  );

  const validArticles = articlesData.filter((article): article is ArticleMetadata => article !== null);
  return validArticles;
};

router.addDefaultHandler(async ({ log, page }) => {
  const currentUrl = page.url();
  const outputPath = getOutputPath(page);
  let has414Error = false;

  page.on("request", async (request) => {
    if (request.resourceType() === "xhr") {
      log.debug(`XHR Request: ${request.url()}`);
      const response = await request.response();
      const responseBody = await response?.text();

      /**
       * When clicking the "load more" button, a page number query parameter is added to the URL.
       * This can cause issues for certain categories (like "Société") where the URL will becomes too long,
       * after a many clicks on the "load more" button, resulting in a 414 "Request-URI Too Long" error from the server.
       */
      if (responseBody?.includes("414 Request-URI Too Long")) {
        log.debug("Detected 414 Request-URI Too Long error!");
        log.debug(`Request URL: ${request.url()}`);
        has414Error = true;
      }
    }
  });

  if (fs.existsSync(outputPath)) {
    const fileContent = fs.readFileSync(outputPath, "utf8");
    const articles = JSON.parse(fileContent);

    if (articles.length > 0) {
      log.info(
        `File ${outputPath} already exists with ${articles.length} articles`
      );
      return;
    }
  }

  log.info(`Processing ${currentUrl}...`);

  while (true) {
    log.error("Has 414 error: " + has414Error);

    const loadMoreButtonHolder = await page.$(".loadmore-holder");
    const loadMoreButton = await page.$(".loadmore-holder a");
    const isLoadMoreButtonDisplayed = await loadMoreButtonHolder?.evaluate(
      (el) => el.classList.contains("display_none")
    );

    if (!loadMoreButton || isLoadMoreButtonDisplayed || has414Error) {
      const articlesMetadata = await getArticlesMetadata(page);
      await saveResults(page, articlesMetadata);
      break;
    }

    await loadMoreButton.click();

    log.debug("Load more button clicked");
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1000);
  }
});
