@0xda6238bd1453f010;

# common struct
enum ActionState {
  new @0;
  changed @1;
  ok @2;
  scheduled @3;
  disabled @4;
  error @5;
  running @6;
}

struct Actor {

  state @0 :State;
  enum State {
    new @0;
    ok @1;
    error @2;
    disabled @3;
  }

  #name of actor e.g. node.ssh (role is the first part of it)
  name @1 :Text;

  #dns name of actor who owns this service
  actorFQDN @2 :Text;

  parent @3 :ActorPointer;

  producers @4 :List(ActorPointer);

  struct ActorPointer {
    actorRole @0 :Text;
    minServices @1 :UInt16;
    maxServices @2 :UInt16;
    auto @3 :Bool;
    optional @4 :Bool;
    argname @5 :Text; # key in the args that contains the instance name of the targets
  }

  actions @5 :List(Action);
  struct Action {
    name @0 :Text;
    #unique key for code of action (see below)
    actionKey @1 :Text;
    period @2 :UInt32; #use j.data.time.getSecondsInHR( to show HR
    log @3 :Bool;
    state @4 :ActionState;
    isJob @5 :Bool;
    timeout @6 :UInt32;
    longjob @7 :Bool = false;

  }

  eventFilters @6 :List(EventFilter);
  struct EventFilter {
      # channel e.g. telegram, leave empty if all
      channel @0 :EventChannel;
      enum EventChannel {
        all @0;
        telegram @1;
        email @2;
        webservice @3;
        blueprint @4;
      }
      # the command that will trigger the execution of the action.
      command @1 :Text;
      # action e.g. start, can be left empty
      actions @2 :List(Text);
      # tags which define sort of filtering e.g. importance:urgent state:down
      tags @3 :Text;
      # secrets
      secrets @4 :List(Text);
      role @5 :Text;
      #if you want to specify a specific service instance
      service @6 :Text;
      #when there is no service but only instances of objects on which actor can work
      instance @7 :Text;
      log @8 :Bool;
  }

  #where does the template come from
  origin @7 :Origin;
  struct Origin {
    #link to git which hosts this template for the actor
    gitUrl @0 :Text;
    #path in that repo
    path @1 :Text;
  }

  flists @8 :List(Flist);
  struct Flist {
      path @0 :Text;
    #   namespace @1 :Text;
    #   mountpoint @2 :Text;
    #   mode @3 :Mode;
    #   storeUrl @4:Text;
    #   content @5 :Text;

    #   enum Mode {
    #     ro @0;
    #     rw @1;
    #     ol @2;
    #   }
  }

  #python script which interactively asks for the information when not filled in
  serviceDataUI @9 :Text;

  serviceDataSchema @10 :Text;

  data @11 :Data; #is capnp struct

  dataUI @12 :Text;

  gitRepo @13 :GitRepo;
  struct GitRepo {
    #git url
    url @0 :Text;
    #path in repo
    path @1 :Text;
  }
}

struct Service {
  #is the unique deployed name of the service of a specific actor name e.g. myhost
  name @0 :Text;

  #name of actor e.g. node.ssh
  actorName @1 :Text;

  #FQDN of actor who owns this service
  actorFQDN @2 :Text;

  parent @3 :ServicePointer;

  producers @4 :List(ServicePointer);
  consumers @12 :List(ServicePointer);

  struct ServicePointer {
    actorName @0 :Text;
    serviceName @1 :Text;
    #domain name of actor who owns this service pointed too
    actorFQDN @2 :Text;
    #defines which rights this service has to the other service e.g. owner or not
    key @3 :Text;
  }

  actions @5 :List(Action);

  struct Action {
    #e.g. install
    name @0 :Text;
    #unique key for code of action (see below)
    actionKey @1 :Text;
    state @2: ActionState;
    log @3 :Bool;
    lastRun @4: UInt32;
    period @5 :UInt32;#use j.data.time.getSecondsInHR( to show HR
    isJob @6 :Bool;
    timeout @7 :UInt32;
    errorNr @8 :UInt8; # count the number of time we retry this action and failed.
    longjob @9 :Bool = false;

  }

  #list of filter statements, when match call service.executeActionService("processEvent",event)
  eventFilters @6 :List(EventFilter);
  struct EventFilter {
      # channel e.g. telegram, leave empty if all
      channel @0 :EventChannel;
      enum EventChannel {
        all @0;
        telegram @1;
        email @2;
        webservice @3;
        blueprint @4;
      }
      # the command that will trigger the execution of the action.
      command @1 :Text;
      # action e.g. start, can be left empty
      actions @2 :List(Text);
      # tags which define sort of filtering e.g. importance:urgent state:down
      tags @3 :Text;
      # secrets
      secrets @4 :List(Text);
      role @5 :Text;
      #if you want to specify a specific service instance
      service @6 :Text;
      #when there is no service but only instances of objects on which actor can work
      instance @7 :Text;
      log @8 :Bool;
  }

  actorKey @7 :Text;

  state @8 :State;
  enum State {
    new @0;
    installing @1;
    ok @2;
    error @3;
    disabled @4;
    changed @5;
  }

  data @9 :Data;
  # bytes version of the content of schema.hrd after translation to canpn

  #schema of config data in textual format
  dataSchema @10 :Text;

  gitRepo @11 :GitRepo;
  struct GitRepo {
    #git url
    url @0 :Text;
    #path in repo
    path @1 :Text;
  }
}
