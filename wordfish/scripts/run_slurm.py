'''
run_slurm.py

A basic script to read in a list of commands, parse into slurm job scripts,
and run the jobs. This will be improved! For now, modify the bottom of the 
script to change the default submission args.

'''

import os
import sys
script_dir = os.path.dirname(os.path.realpath(__file__))
job_dir = "%s/.job" %(script_dir)
out_dir = "%s/.out" %(script_dir)

### MODIFY SUBMISSION ARGS HERE ###########################################
queue_name = "normal"
time = "2-00:00"
memory = 64000
##############


if len(sys.argv) < 2:
    print('Please provide job file with list of single commands as input.')

else:
    jobfile = sys.argv[1]

    if not os.path.exists(job_dir):
        os.mkdir(job_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # Read in the jobfile, and write a job for each line
    filey = open(jobfile,"rb")
    commands = filey.readlines()
    filey.close()

    # Name the job based on input script
    name = os.path.basename(jobfile).split(".")[0]

    for c in range(len(commands)):
        command = commands[c]
        jobfile = open("%s/%s_%s.job" %(job_dir,name,c),'w')
        jobfile.writelines("#!/bin/bash\n")
        jobfile.writelines("#SBATCH --job-name=%s_%s.job\n" %(name,c))
        jobfile.writelines("#SBATCH --output=%s/%s_%s.out\n" %(out_dir,name,c))
        jobfile.writelines("#SBATCH --error=%s/%s_%s.err\n" %(out_dir,name,c)) 
        jobfile.writelines("#SBATCH --time=%s\n" %(time)) 
        jobfile.writelines("#SBATCH --mem=%s\n" %(memory))   
        jobfile.writelines(command)  
        jobfile.close()
        os.system('sbatch -p %s -n 1 %s/%s_%s.job' %(queue_name,job_dir,name,c))
