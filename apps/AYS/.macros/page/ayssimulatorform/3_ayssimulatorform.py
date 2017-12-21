def main(j, args, params, tags, tasklet):
    page = args.page
    from JumpScale9Portal.portal.docgenerator.form import Form
    import yaml

    query_params = args.requestContext.params
    repo = args.getTag('repo') or query_params.get('repo', None)
    action = query_params.get('action', '')
    role = query_params.get('role', '')
    instance = query_params.get('instance', '')
    force = query_params.get('force', '')

    form = Form(id='action-simulate',
                  header="Simulate Action",
                  submit_url="#?repo=%s" % repo,
                  submit_method="get",
                  navigateback=False,
                  reload_on_success=False,
                  showresponse=False,
                  clearForm=False)

    form.addHiddenField('repo', repo)
    form.addText(label="Action Name", name='action', required=True, type='text', value=action, placeholder='install')
    form.addDropdown(label="Force", name='force', required=True, options=[('false', 'False'), ('true', 'True')])
    form.addText(label="Role", name='role', required=False, type='text', value=role, placeholder='')
    form.addText(label="Instance", name='instance', required=False, type='text', value=instance, placeholder='')
    form.addButton(type='submit', value='simulate')
    if action or role or instance:
        form.addButton(type='reset', value='reset', link='/%s?repo=%s' % (args.requestContext.path, repo))

    form.write_html(page)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
