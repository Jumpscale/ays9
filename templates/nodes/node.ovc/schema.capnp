
@0xd37ff48ad935931f;
struct Schema {
	description @0 :Text;
	bootdiskSize @1 :Int64 = 10;
	memory @2 :Int64 = 1;
	sizeID @3 :Int64 = -1;
	osImage @4 :Text = "Ubuntu 15.10";
	ports @5 :List(Text);
	machineId @6 :Int64 = 0;
	ipPublic @7 :Text;
	ipPrivate @8 :Text;
	sshLogin @9 :Text;
	sshPassword @10 :Text;
	vdc @11 :Text;
	disk @12 :List(Text);
	sshkey @13 :Text;
	sshAddr @14 :Text;
	sshPort @15 :Int64 = 0;
	ovfLink @16 :Text;
	ovfUsername @17 :Text;
	ovfPassword @18 :Text;
	ovfPath @19 :Text;
	ovfCallbackUrl @20 :Text;
	stackID @21 :Int64 = -1;
	vmHistory @22 :Text;
	uservdc @23 :List(UserVdcEntry);
	cloneName @24 :Text;
	snapshots @25 :List(Text);
	snapshotEpoch @26 :Text;
	
	struct UserVdcEntry {
		name @0 :Text;
		accesstype @1 :Text = "R";
	}
}
