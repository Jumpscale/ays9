## How to get an OAuth Authorization Code

An OAuth authorization code is the token you receive from ItsYou.online when using the **Authorization Code Flow**, confirming that the user has approved that the requesting (server) application can interact with ItsYou.online on behalf of the user, e.g. to access the ItsYou.online profile of the user. This is one of the OAuth 2.0 grand types supported by ItsYou.online. The authorization code flow grant type is the most commonly used grand type because it is optimized for server-side applications where **Client Secret Confidentiality** can be maintained, meaning that the server application requesting the authorization code doesn't need to know the client secret of the user or organization on behalf of which it needs to get things done. This is achieved through a redirection-based flow, where the server application interacts with the user-agent (e.i. the user's web browser) for receiving the authorization code, routed through the user-agent.

Receiving the OAuth authorization code is a three steps process:

1. First, the server application redirects the user to ItsYou.online via the **authorization code link**:

   ```
   curl -d "response_type=code&client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}&scope=user:name&state={STATE}"
        https://itsyou.online/v1/oauth/authorize
   ```

2. The user authorizes the request and is then redirected to the callback address of the requesting server

3. The server application receives the OAuth authorization code as part of the redirect URL of the second step, this redirect URL looks like:

   ```
   https://petshop.com/callback?code=AUTHORIZATION_CODE&state=STATE
   ```

Your server application can then use this OAuth authorization code to request an **OAuth Access Code** in order to actually interact on behalf of the user with ItsYou.online. In the context of the Cockpit your server application will use the access code to request a JWT from ItsYou.online. This JWT is needed to call the Cockpit APIs on behalf of the user.

Alternatively you can also request a JWT from ItsYou.online in order to interact with the Cockpit API on behalf of the organization, this is done by first request the **OAuth Access Code** through the **Client Credentials Flow**.

Both cases are discussed in the sections about [How to get an OAuth access code](../Get_oauth_access_token/Get_oauth_access_token) and [How to get a JWT](../Get_JWT/Get_JWT.md). Also see the [ItsYou.online documentation](https://www.gitbook.com/book/gig/itsyouonline/details) and the [ItsYou.online API Console](
https://itsyou.online/apidocumentation) for more information.
