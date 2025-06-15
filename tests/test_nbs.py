def main():

    from nbdev.config import get_config
    from nbdev.doclinks import nbglob
    from fastcore.foundation import working_directory
    from nbdev.test import test_nb
    import os
    import sys

    skip_flags = get_config().tst_flags.split()
    force_flags = []
    files = nbglob(None, as_path=True)
    files = [f.absolute() for f in sorted(files)]
    if len(files)==0: print('No files were eligible for testing')

    wd_pth = get_config().nbs_path
    results = []

	# run nbdev_test
    with working_directory(wd_pth if (wd_pth and wd_pth.exists()) else os.getcwd()):
        for file in files:
            print(file)
            result = test_nb(file, skip_flags=skip_flags, force_flags=force_flags, basepath=get_config().config_path, do_print=True)
            results.append(result[0])
    if all(results): 
        print("Success.")
    else: 
        _fence = '='*50
        failed = '\n\t'.join(f.name for p,f in zip(results,files) if not p)
        sys.stderr.write(f"\nnbdev Tests Failed On The Following Notebooks:\n{_fence}\n\t{failed}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()