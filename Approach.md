# National Health Directory Approach and Strategy

## Strategy

### Foundational Technology Strategy

 • No Proprietary Lock-in: Avoid proprietary technologies, platforms, or services.
 • Long-Term Sustainability: Plan for a 50-year timeline using mature, widely adopted technologies. Plan in accordance with the [Lindy Effect](https://en.m.wikipedia.org/wiki/Lindy_effect)
 • Preference for Old and Stable Tools: Prioritize tools with 10+ years of proven utility.
- Use the honeycomb approach. Create small software modules that have consistent frameworks to leverage AI (worker bees) to implement complexity only ‘within’ each honeycomb.
 


### Honeycomb approach to Health IT complexity

- Health IT complexity tends to be in combinatorics of small weird problems and requirements creating a tangled and unmanaged whole.
- This is exactly the type of complexity that AI coding tools currently struggle with.
- This makes “Detail denial” an especially dangerous mistake.
- To solve Health IT problems each type of problem needs to be well framed and boxed in, so that an AI can successfully ignore the complexity of the larger system while it works on a single part of the whole. 
- Keep the abstraction layers as thin as possible. All abstractions are leaky. But thin ones keep the underlying complexity close to the surface. To put this another way: automations should tend to make coding easier but never to actually ‘avoid’ coding.


### Data Processing and Integration

 • Universal Execution Contexts: Ensure support in Python, Jupyter Notebooks, Unix CLI, and SAS. Data pipeline options that do not support all of these and all potential future data contexts are non-starters.
 • SQL-Centric Processing: Use plain SQL for transformations, interleaved with Python. 
 - When it is not possible to simply hand code the SQL steps a ‘compile to sql’ approach should be taken
 - There are numerous cases where a data transformation must be in R, Pandas or SAS data steps. But this should never be based on mere programmer preference, and the reasons for the exceptions should be clearly documented.

### Scalability and Accessibility

- Dual Schema Design: Separate public and private schemas.
- Downloadable Data: Support bulk access with moderate API load.

### Compatibility Requirements

 • NPPES Backward Compatibility:
	 • Reproduce NPPES flat files
	 • Maintain entity types, Medicare codes, and NUCC taxonomy
 • Claims & Regulatory Continuity:
	 • Medicaid ACOs, QHPs, FQHCs, and legacy systems

### FHIR Compliance

 • Strict Schema Alignment: Must pass validation against FHIR schemas.
 • Correct Resource Use: Use FHIR elements per spec (e.g., PractitionerRole).

### Data Quality and Feedback

 • Validate When Possible: Fully validate or track confidence levels.
 • User Feedback Channels:
 • Patient-facing UX for data accuracy
 • Token-limited write-back API for structured corrections

### Decision-Making Heuristics

 • Reliable > Experimental: Use proven tools.
 • Ensure backward/future compatibility.

## Engineering Process Philosophy

### Git-Based Collaboration

 • Use Git/GitHub workflows.
 • Clean, small PRs preferred, but large PRs accepted when necessary.
 - Convert the biggest pull requests into separate modules. Honeycomb approach.
 • Emphasize clarity and forward momentum.

### Test-Driven Expectations

 • Expectations Before APIs: Define tests before implementation.
 • Test-Driven Data Models: Built alongside ETLs with validations.
 • ETL Resilience by Design:
 • Validate assumptions
 • Break early and loudly on errors

### Anti-Fragile Infrastructure

 • Fail Loudly, Recover Quickly: Small, fragile components improve overall system robustness.
 • Continuous Feedback Loops: Tests and checks detect degradations early.
 - Leverage lots of different kinds of tests, generally preferring higher level tests that will detect between system failures
 - Specifically leverage data expectation tests to avoid pipeline technical debt
 - Data expectations should make us aware of healthcare ecosystem changes as much as data etc errors. I.e. if all of the pediatricians are suddenly men. This could mean a dramatic change in the healthcare system or a broken import script.

### Legacy Respect: The Joel on Software Principle

 • No Clean Slate Rebuilds: Avoid rewrites; understand existing code first.
 • Inherited Code is Knowledge: Features represent hard-earned lessons.
 • Respect Before Refactor: Prior design is valid until proven otherwise.
 • Avoid Reinventing Mistakes: Rewrites risk losing key insights.
 • Evolve, Don’t Replace: Improve incrementally.

