EMAIL=SET_THIS
PASSWORD=SET_THIS
SOURCE=SET_THIS

curl -X POST https://www.google.com/accounts/ClientLogin -d Email=$EMAIL -d Passwd=$PASSWORD -d source=$SOURCE -d accountType=HOSTED_OR_GOOGLE -d service=ac2dm
