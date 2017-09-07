# Actor Schema

- **schema.capnp**

  - Which is the schema for the service instance metadata relevant for an instance of the service

  - Has parameter definitions used to configure the service

  - Example:

    ```
    @0x8e49424dcf7a20be;
    struct Schema {
    	os @0 :Text;
    	fs @1 :List(Text);
    	docker @2 :Text;
    	hostname @3 :Text;
    	image @4 :Text = "ubuntu";
    	ports @5 :List(Text);
    	volumes @6 :List(Text);
    	cmd @7 :Text;
    	sshkey @8 :Text;
    	id @9 :Text;
    	ipPublic @10 :Text;
    	ipPrivate @11 :Text;
    	sshLogin @12 :Text;
    	sshPassword @13 :Text;

    }
    ```
