from send_email import *

def koaxfr(instrObj):
    """
    Transfers the contents of outputDir to its final destination.
    Location transferring to is located in config.live.ini:
        KOAXFR:server
        KOAXFR:account
        KOAXFR:dir
    Email is sent to KOAXFR:emailto upon successful completion
    Email is sent to KOAXFR:emailerror if an error occurs
    """

    import configparser
    import os

    instr = instrObj.instr.upper()

    # Directory that will be transfered

    fromDir = instrObj.dirs['output']

    # Verify that the directory to transfer exists

    if not os.path.isdir(fromDir):
        instrObj.log.error('koaxfr.py directory ({}) does not exist'.format(fromDir))
        return False

    # Read config file

    import configparser
    config = configparser.ConfigParser()
    config.read('config.live.ini')
    emailFrom = config['KOAXFR']['EMAILFROM']
    emailTo = config['KOAXFR']['EMAILTO']

    # Verify that there are FITS files

    count = len([name for name in os.listdir(instrObj.dirs['lev0']) if name.endswith('.fits.gz')])
    if count == 0:
        instrObj.log.error('koaxfr.py no FITS files to transfer')
        # Send email verifying transfer complete
        subject = ''.join((instrObj.utDate.replace('-', ''), ' ', instr))
        message = ''.join(('No metadata for ', instrObj.utDate.replace('-', '')))
        instrObj.log.info('koaxfr.py sending no data email to {}'.format(emailTo))
        send_email(emailTo, emailFrom, subject, message)
        return True

    # Configure the transfer command

    server = config['KOAXFR']['SERVER']
    account = config['KOAXFR']['ACCOUNT']
    toDir = config['KOAXFR']['DIR']
    toLocation = ''.join((account, '@', server, ':', toDir, '/', instr))
    instrObj.log.info('koaxfr.py transferring directory {} to {}'.format(fromDir, toLocation))
    instrObj.log.info('koaxfr.py rsync -avz {} {}'.format(fromDir, toLocation))

    # Transfer the data

    import subprocess as sp
    xfrCmd = sp.Popen(["rsync -avz " + fromDir + ' ' + toLocation],
                      stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    output, error = xfrCmd.communicate()
    if not error:
        # Send email verifying transfer complete
        instrObj.log.info('koaxfr.py sending email to {}'.format(emailTo))
        subject = ''.join(('lev0 ', instrObj.utDate.replace('-', ''), ' ', instr))
        message = 'lev0 data successfully transferred to koaxfr'
        send_email(emailTo, emailFrom, subject, message)
        return True
    else:
        # Send email notifying of error
        emailError = config['KOAXFR']['EMAILERROR']
        instrObj.log.error('koaxfr.py error transferring directory ({}) to {}'.format(fromDir, toLocation))
        instrObj.log.error('koaxfr.py sending email to {}'.format(emailError))
        message = ''.join(('Error transferring directory', fromDir, ' to ', toDir, '\n\n'))
        send_email(emailError, emailFrom, 'Error - koaxfr transfer', message)
        return False

