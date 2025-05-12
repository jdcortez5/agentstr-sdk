from dotenv import load_dotenv
import os

from nwc import processNWCstring, listTx, getBalance, makeInvoice, checkInvoice

load_dotenv()

nwc_info = processNWCstring(os.environ['NWC_CONN_STR'])

#print(nwc_info)
#print(listTx(nwc_info))
#print(getBalance(nwc_info))

#print(makeInvoice(nwc_info, amt=1000, desc="Test invoice"))
print(checkInvoice(nwc_info, invoice='lnbc10u1p5p043cdq523jhxapqd9h8vmmfvdjsnp4q2u2qkyq5tzswac75yqk8cyqavmhq9q3j2vdxh946vxxhzjyk8sn6pp59cs7we2z0s5859zv4225y4a4xvcsvtevvn7zgz9tvh897qyqzpvqsp5jtg5h6m6akaeepk4ekye45xda4up7585vwcgz05nacpyp9t78zeq9qyysgqcqpcxqyz5vq857xs8y4zxxwwnqhh55vz6afq8jhref73tj4rpwrg8zvspcp25n9n7r74dr55xllyul7vl75f974xkuxrxyvgpwe7yqj2vmras24q7qpq2ch6z'))