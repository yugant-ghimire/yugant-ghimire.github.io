**Reference Article** : https://www.braintrust.dev/blog/agent-while-loop

- No need to push in too many arguments into a tool call. Breakdown the tool call into multiple simple ones. Similar to defining the scope of function with only one task, break down the context of the API call into maybe just one tool call with simple scope rather than multiple large ones which overloads the whole tool call. This loses context and decreases the clarity. 
- Evaluation as a foundation:
	- Create a representative dataset that you can evaluate and library of scorers. 
	- it should be able to verify that the agent can complete various ambitious tasks 
	- Run more evals on the LLM's wrong tool call to define specifically where it fails. (helps with creating better context/prompt)
- Keep it simple: An agent is an LLM, system prompt and tool call
	- making it more complex with other frameworks will lead to tech debt
	- need to change with evolving of the LLM
- Frameworks can be valuable for specific use cases, but the core components remain consistent: a good prompt that defines the agent's role and capabilities, a small set of clean tools designed for the agent's mental model, a transcript window that maintains conversation state, and a while loop that orchestrates everything.

