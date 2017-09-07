## Cockpit JWT

Even though the OAuth token support works great for applications that need to access the information of a user, when passing on some of these authorizations to a third party service it is not a good idea to pass on your token itself.

The token you acquired might give access to a lot more information that you want to pass on to the third party service and it is required to invoke itsyou.online to verify that the authorization claim is valid.

For these use cases, itsyou.online supports JWT RFC7519.

You can generate JWT token by selecting **JWT** from the navigation menu under **AYS Portal**. On this page click the **Generate JWT token** to get your JWT token.

You can now pass this token to the API client to be able to use the REST api.
