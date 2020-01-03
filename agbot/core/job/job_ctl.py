class JobCtl:

    def __init__(self,
                 job_id: str,
                 desc: str):
        self.job_id = job_id
        self.desc = desc

    def __str__(self):
        repr_str = "<JobCtl(job_id={job_id}, desc={desc})>".format(job_id=self.job_id, desc=self.desc)
        return repr_str

    def __repr__(self):
        return self.__str__()


class FileJobCtl(JobCtl):
    attachment_dir: str
    job_dir = ...  # type: str

    def __init__(self,
                 job_id: str,
                 desc: str,
                 job_dir: str,
                 attachment_dir: str):
        JobCtl.__init__(self, job_id, desc)
        self.job_dir = job_dir
        self.attachment_dir = attachment_dir

    def __str__(self):
        repr_str = ("<JobCtl(job_id={job_id}, desc={desc}, job_dir={job_dir})>".
                    format(job_id=self.job_id, desc=self.desc, job_dir=self.job_dir))
        return repr_str

    def __repr__(self):
        return self.__str__()


