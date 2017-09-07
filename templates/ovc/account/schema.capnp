
@0xdd89b76472682068;
struct Schema {
	description @0 :Text;
	g8client @1 :Text;
	accountusers @2 :List(UserVdcEntry);
	accountID @3 :Int64 = 0;
	maxMemoryCapacity @4 :Int64 = -1;
	maxCPUCapacity @5 :Int64 = -1;
	maxNumPublicIP @6 :Int64 = -1;
	maxDiskCapacity @7 :Int64 = -1;
	consumptionFrom @8 :Int64;
	consumptionTo @9 :Int64;
	consumptionData @10 :Data;

	struct UserVdcEntry {
		name @0 :Text;
		accesstype @1 :Text;
	}
}
