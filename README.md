# Domain Checker
Domain Checker is a simple tool for monitoring the availability of domains and sending notifications
via email and/or Discord. This tool is packaged as a Docker container for easy deployment in any environment.

# Docker Hub
  This image is also available on Docker Hub: https://hub.docker.com/r/cyberbytecraft/domain-checker


  
# Features
 - Monitor domain availability
 - Send notifications via email and/or Discord
 - Easily configurable through environment variables
 - Dockerized for simple deployment
# Usage
   - Run the Docker Container:

```bash
-docker run --name domain-checker \
-e POSTFIX_MYHOSTNAME="mail.pushedgaming.at" \
-e POSTFIX_MYDOMAIN="pushedgaming.at" \
-e EMAIL_FROM="domainchecker@pushedgaming.at" \
-e EMAIL_TO="admin@pushedv.de" \
-e NOTIFICATION_METHODS="email" \
-e DOMAINS="withercraft.de" \
-e COOLDOWN=3600 \
-e LOG_LEVEL="INFO" \
--restart always \
cyberbytecraft/domain-checker:0.03
```


# Environment Variables



#   POSTFIX_MYHOSTNAME
 - Set the hostname for the Postfix server.
 - Example: "mail.pushedgaming.at"

#   POSTFIX_MYDOMAIN
 - Set the domain name for the Postfix server.
 - Example: "pushedgaming.at"

#   EMAIL_FROM
 - Specify the sender email address.
 - Example: "domainchecker@pushedgaming.at"

#   EMAIL_TO
 - Specify the recipient email address.
 - Example: "admin@pushedv.de"

#   NOTIFICATION_METHODS
 - Specify the notification methods, e.g., email or Discord.
 - Example: "email,discord"

#   DOMAINS
 - List the domains to monitor, separated by commas.
 - Example: "withercraft.de"

#   COOLDOWN
 - Set the cooldown time in seconds between domain checks.
 - Example: 3600

#   LOG_LEVEL
 - Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
 - Example: "INFO"

