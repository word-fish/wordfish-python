import os

#TODO: need to think of how to template-ize this!

inputs = [SUB_INPUTS_SUB]
outfolder = "[SUB_OUTPUTFOLDER_SUB]"

for i in inputs:
    if not os.path.exists("%s/%s_dict.pkl" %(outfolder,i)):
        jobfile = open(".job/%s.job" %i,'w')
        jobfile.writelines("#!/bin/bash\n")
        jobfile.writelines("#SBATCH --job-name=%s.job\n" %(i))
        jobfile.writelines("#SBATCH --output=.out/%s.out\n" %(i))
        jobfile.writelines("#SBATCH --error=.out/%s.err\n" %(i)) 
        jobfile.writelines("#SBATCH --time=2-00:00\n") 
        jobfile.writelines("#SBATCH --mem=12000\n")   
        jobfile.writelines("python [SUB_SCRIPT_SUB] %s %s\n" %(i,outfolder))  
        jobfile.close()
        os.system('sbatch -p russpold .job/%s.job' %disorder)
