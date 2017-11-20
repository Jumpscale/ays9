def install(job):
    import time
    timeData = [data for data in job.service.model.data.timeData]
    timeData.append(int(time.time()))
    job.service.model.data.timeData = timeData
    job.service.save()
    raise Exception("To test scheduler retries configuration")
