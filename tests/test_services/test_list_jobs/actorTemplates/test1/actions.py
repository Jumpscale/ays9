def install(job):
    service = job.service
    j.tools.async.wrappers.sync( service.executeAction('printx', context=job.context, args={"tags":['a', 'C', 'b']}))

def printx(job):
    print("Executing printx in test1")
