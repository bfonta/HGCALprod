
import os
import argparse
from itertools import product
from subprocess import Popen, PIPE

def check(folder):
    """Check if folder exists. If it does, ask to remove it."""
    if os.path.isdir(folder):
        inp = input("Folder log '{}' exists. Do you wish to remove the log folder? [y/n] ".format(folder))
        while True:
            if inp == 'y':
                proc = Popen("rm -r {}".format(folder), shell=True, stdout=PIPE, encoding='utf-8')
                proc.wait()
                break
            elif inp == "n":
                raise RuntimeError("Exit.")
            else:
                inp = input("Please type 'y' or 'n' ")
    os.makedirs(folder)

class dot_dict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def step2_filelist(folder, nfiles, inspect=False):
    """Get files which exist inside step2 folder."""
    if inspect: # check if the files are sane
        import ROOT
        
    fileList = []
    fpath = os.path.join("/data_CMS/cms/", os.environ['USER'], folder, "step2")
    for filename in os.listdir(fpath):
        if inspect:
            inFile = ROOT.TFile.Open(fpath+filename , "READ")
            if(inFile.GetListOfKeys().Contains('Events')):
                idx = filename.split('_')[1].split('.')[0]
                fileList.append(idx)
        else:
            idx = filename.split('_')[1].split('.')[0]
            fileList.append(idx)

        if len(fileList) >= nfiles:
            break

    fileList.sort(key=lambda x: float(x)) # sort numerically
    return fileList

def submit(args):
    """Create HTCondor submission files and launch the submission."""
    jobs_f = "condor"
    logs_f = os.path.join(jobs_f, "log_step3_" + args.data_folder + args.tag)
    check(logs_f)

    step2_l = step2_filelist(args.data_folder, args.nfiles)
    with open(os.path.join(logs_f, "step2UsedFiles.txt"), 'w') as afile:
        afile.write('\n'.join(str(x) for x in step2_l))

    sub_file = os.path.join(logs_f, "condor.sub")
    batch_logs = os.path.join(logs_f, "$(Step2)_CDens$(CDens)_CDist$(CDist)_KDens$(KDens)")
    with open(sub_file, "w") as afile:
        mes = ("executable  = {}/batchScript_onlystep3.sh".format(jobs_f),
               "arguments   = {} {} $(Step2) {} $(CDens) $(CDist) $(KDens)"
               .format(args.data_folder, args.sample_name, args.tag),
               "universe    = vanilla",
               "output      = {}.out".format(batch_logs),
               "error       = {}.err".format(batch_logs),
               "log         = {}.log".format(batch_logs),
               "",
               "+JobFlavour = \"tomorrow\"",
               "+JobBatchName = \"Scan_{}{}\"".format(args.data_folder, args.tag),
               "",
               "getenv = true",
               "",
               "T3Queue = {}".format(args.queue),
               "WNTag=el7",
               "+SingularityCmd = \"\"",
               "include : /opt/exp_soft/cms/t3/t3queue |",
               "\n")
        afile.write('\n'.join(mes))

        mes = "queue Step2, CDens, CDist, KDens from (\n"
        for item in product(step2_l, args.cdens, args.cdist, args.kdens):
            item2 = '  ' + ', '.join(str(it) for it in item) + '\n'  
            mes += item2.replace('.', 'p').replace('-', 'm')
        mes += ')'
        afile.write(mes)

    if not args.dryrun:
        subm_comm  = 'condor_submit {}'.format(sub_file)
        pipeopt = dict(shell=True, stdout=PIPE, encoding='utf-8')
        pipe = Popen(subm_comm, **pipeopt)
    else:
        print("Dry-run! Files created but not launched.")

if __name__ == "__main__":
    # voms-proxy-init --rfc --voms cms -valid 192:00
    # source /opt/exp_soft/cms/t3/t3setup

    parser = argparse.ArgumentParser(description='Submit only step3.')
    parser.add_argument('-f', "--data_folder", required=True, help="Data folder")
    parser.add_argument('-s', "--sample_name", required=True, help="Sample name")
    parser.add_argument('-t', "--tag", required=False, default='',
                        help="Tag for similar runs")
    parser.add_argument("--cdens", "--criticalDensity", nargs='+', default=[0.6],
                        help="Critical density in GeV")
    parser.add_argument("--cdist", "--criticalEtaPhiDistance", nargs='+', default=[0.025],
                        help="Minimal distance in eta,phi space from nearestHigher to become a seed")
    parser.add_argument("--kdens", "--kernelDensityFactor", nargs='+', default=[0.2],
                        help="Kernel factor to be applied to other LC while computing the local density")
    parser.add_argument("--nfiles", "--nstep2_files", default=2, type=int,
                        help="Number of step2 files to consider")
    parser.add_argument('-q', "--queue", default="short", choices=("short", "long"),
                        help="HTCondor queue type")
    parser.add_argument('-n', "--dryrun", help="Dry-run", action="store_true")

    FLAGS = parser.parse_args()
    submit(dot_dict(vars(FLAGS)))
