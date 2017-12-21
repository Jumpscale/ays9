def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'test': ['install']

    }



def test(job):
    """
    Test list jobs
    """
    model = job.service.model
    model.data.result = RESULT_OK % job.service.name
    failures = []
    # HERE create run in listjobs repo
    action = "printx"
    actor = "test1"
    tags = "a,C"
    fields = "tags"
    state = "ok"
    try:
        repo = 'listjobs'
        cl = j.clients.atyourservice.get().api.ays
        cl.executeBlueprint(data=None, repository=repo, blueprint='create.yaml')
        jobs = cl.listJobs('test', query_params="actor={}}&state={}&action={}&tags={}&fields={}".format(actor, state, action, tags, fields)).content.decode()
        jobs = json.loads(printx_jobs)
        for job in jobs:
            if job['action'] != action or job['actor'] != actor or job['state'] != state:
                model.data.result = "FAILED data returned dosn't match the request"
                break
        else:
            for tag in tags.split(","):
                if tag not in job['tags']:
                    model.data.result = "FAILED tag {} not found in job tags".format(tag)
                    break
            else:
                model.data.result = RESULT_OK % 'Test listJobs Executed succesfully'
    except:
        model.data.result = RESULT_ERROR % str(sys.exc_info()[:2])
    finally:
        job.service.save()
        cl.destroyRepository(data=None, repository=repo)
