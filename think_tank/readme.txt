# Our Think Tank is our Research Team. This is how we get things done. Each member has a very specific job. This keeps tasks focused, and keeps models small, nimble and prevents overloading the context window or desiging an agent that is too broad in scope and loses focus.

The think tank is comprised of 3 separate agents:

1) A1 (Agent 1) Codename: SCUBA - Retriever/Scraper - SCUBA is a python script utilizing either Crawl4AI or LangChain (TBD) coupled with a fast, local model. 

SCUBA SKILLS:   + web searching
                + scraping raw md files form top 10 results
                + trim out tracking/cookies & fluff

              SUPERPOWER(?): Evasion; SCUBA knows what to do to evade captcha, bot detection, spam detection, or VPN blocks. This will be done either natively in the code (agent will know how to solve captchas) or we will have a specific tool call or separate agent which only solves captchas for SCUBA. 

2) A2 (Agent 2) Codename: MOZART - The synthesizer - MOZART is a composer. He takes the raw text block, groups the data into thematic caregores, extracts hard metrics, and highlights apparent market opportunities or technical hurdles

MOZART SKILLS:  + sorting & categorizing
		+ creating relative, related data chunks/blocks
		+ extracting metrics
		
	     SUPERPOWER(?): Niche/market potential, obstacles: MOZART is able to discover, through his synthesis process, outlier or niche markets that might have otherwise gone unnoticed. He takes the data and draws parrellels, finds patterns, and makes suggestions. He is also able to find flaws, failsafe plans that might avoid problems, and potential drawbacks or obstacles we might face. While he is moderately good at this, his primary job is sorting and drawing parrelels. The final judgement is made by PNUT, the critic and final agent that judges the synthesis or composition of notes/data.

3) A3 (Agent 3) Codename: PNUT - The judge & critic. PNUT makes the final decision on this pipeline, as the logical agent. He is cold and logical, finding the logical gaps, unverified claims, or missing counter-arguments. It pushes a revised version back into a final clean .md report file. 

PNUT SKILLS:	+ purely factual, no care for "feelz"
		+ balanced & nuanced..doesn't disagree just for sake of it
		+ Devil's Advocate at times
		
              SUPERPOWER(?): PNUT is able to revise the final output and send it back to the beginning for iteration. His final report creates a judgementday.md file which is looked at by the architect & human to consider. In some occasions, where we just want to keep sharpening and iterating on a deep analysis, he can shift the search scrape parameters or recommend more specific rabbit holes to explore for missed opportunities. Actually, he probably does this anyways, this is how the think tank becomes self-contained and self-iterating. 

We might want to generate a confidence score from PNUT; once he has a confidence score that meets our project threshold (say 95% if that is what our goal is) then he sends an alert to the human or architect or both to deliver the think tank's final findings and research data points. 

At this point, the human and architect brainstorm if needed and devise more tasks for the think tank. If the research for the current project is finished, general web scraping & research can take place. We should always have some project going on here 24/7 or it's not performing correctly!

See folders for individual prompts, LoRAs, weights, etc.
