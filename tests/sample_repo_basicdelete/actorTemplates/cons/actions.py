def processChange(job):
    args = job.model.args
    category = args.pop('changeCategory')    
    if category=="links":
        producers=args.pop("producer_removed", None)
        print("producer was removed ", producers)
        
