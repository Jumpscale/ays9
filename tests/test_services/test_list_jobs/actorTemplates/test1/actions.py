def install(job):
    service = job.service
    service.executeAction('printx', context=job.context, args={"tags":['a', 'C', 'b']})

def printx(job):
    print("Executing printx in test1")
