# DEAD END
The pivot aggregator has a login through the email page, so it isn't possible to use the link through the forwarded email. It will default to the login page instead, and that is not possible to bypass. I missed this when I was originally checking the email link to the grants as my laptop seems to have completed a shibboleth login without actually logging me into my account granting me access to the page without showing me as logged in on that page. 

# MACSS Grant LLM Filter

This project uses GPT4 to read though grant texts and filter out grants that do
not meet the required criteria. For grants that do meet criteria, it produces 
a summary of the grant and sends it as an email for human review.

If you have mamba installed on your machine, you can use the following bash script to install the environment.
```
$ bash install_env.sh
```

## Aggregator and Grant Notes

General notes on aggregator services and grants are included in the [research_notes.md](research_notes.md) file.