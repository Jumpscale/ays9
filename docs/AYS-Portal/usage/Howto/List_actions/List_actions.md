## List all available actions for a service instance

Two ways of listing all available actions for a service instance are documented here:
- [Using the curl](#curl)
- [Using the API Console](#api-console)

<a id="curl"></a>
### Using curl

curl -X GET
     -H "Authorization: bearer JWT"  /
     -d "action=install&async=true&force=false"
     https://BASE_URL/api/ays/repository/REPOSITORY-NAME/service/SERVICE-ROLE/INSTANCE-NAME/action


<a id="api-console"></a>
### Using the API Console

There is a Cockpit API for that which you can easily test using the **API Console**:

![](list-actions-API.png)

You will first need to acquire an JWT.

Fill out the form:

![](try.png)

When you click **GET** following request will be send:

![](request.png)

And the response:

![](response.png)

For information about the **API Console** go [here](../../API_Console/API_Console.md).
